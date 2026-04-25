import csv
import time
import os
import random
import requests
from bs4 import BeautifulSoup
import re
import json
import threading
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Pre-compiled regex patterns (compiled once at import time, not per URL) ---
RE_WARNING_TOP       = re.compile('DrugOverview__warning-top')
RE_WARNING_TAG       = re.compile('DrugOverview__warning-tag')
# Fact box: real class is DrugFactBox__*, not FactBox__*
RE_FACT_BOX          = re.compile('DrugFactBox__content')
RE_FACT_ROW          = re.compile('DrugFactBox__fact-row')
RE_FACT_KEY          = re.compile('DrugFactBox__col-left')
RE_FACT_VAL          = re.compile('DrugFactBox__col-right')
RE_INTERACTION_WRAP  = re.compile('DrugInteraction__drug-interaction-wrapper')
RE_INTERACTION_PANEL = re.compile('DrugInteraction__interaction-panel')
RE_DRUG_NAME         = re.compile('DrugInteraction__drug-name')
RE_SEVERITY          = re.compile('DrugInteraction__severity-text')
RE_DRUG_DIV          = re.compile('DrugInteraction__drug___')
RE_DESC_CONTENT      = re.compile('ProductDescription__description-content', re.I)
RE_OVERVIEW_CONTENT  = re.compile('DrugOverview__content')
RE_SUBSTITUTE_ITEM   = re.compile('SubstituteItem__item')
RE_SUB_NAME          = re.compile('SubstituteItem__name')
RE_SUB_MFR           = re.compile('SubstituteItem__manufacturer-name')
RE_SUB_PRICE         = re.compile('SubstituteItem__price')
RE_PRODUCT_INTRO     = re.compile('Product introduction', re.I)
RE_HOW_WORKS         = re.compile('How .* works', re.I)
RE_BENEFITS_OF       = re.compile('Benefits of', re.I)
RE_ALL_SUBS          = re.compile('All substitutes', re.I)
RE_USER_FEEDBACK     = re.compile('style__feedback-container')
RE_STORE_BELOW       = re.compile('Store below', re.I)
RE_REFERENCES        = re.compile('DrugPage__reference')
RE_MARKETER          = re.compile('DrugPage__compliance-info-wrapper')
RE_QUICK_TIPS        = re.compile('Quick tips', re.I)
RE_PAIN              = re.compile('ANTI INFECTIVES', re.I)
RE_INTERACTION_H2    = re.compile('interaction', re.I)
RE_FAQ_TILE          = re.compile('Faqs__tile')
RE_FAQ_QUES          = re.compile('Faqs__ques')
RE_FAQ_ANS           = re.compile('Faqs__ans')
RE_HOW_WORKS_H2      = re.compile('works', re.I)

# Thread lock to prevent multiple threads from writing to the CSV at the exact same microsecond
csv_lock = threading.Lock()
processed_count = 0
total_urls = 0

# Thread-local storage for requests.Session
thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

def extract_medicine_details(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    session = get_session()
    
    for attempt in range(3):
        try:
            response = session.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"HTTP {response.status_code} for {url}. Retrying...")
                time.sleep(2)
                continue
            
            html = response.text
            # Use lxml parser which is significantly faster than html.parser
            soup = BeautifulSoup(html, "lxml")

            # 1. Brand Name
            title = soup.find('h1', class_='DrugHeader__title-content___2ZaPo')
            brand_name = title.text.strip() if title else ""

            # 2. Composition (Salt)
            salt_div = soup.find('div', class_='saltInfo')
            composition = salt_div.text.strip() if salt_div else ""

            # 3. Manufacturer
            manufacturer = ""
            for elem in soup.find_all('div', class_='DrugHeader__meta-value___vqYM0'):
                a_tag = elem.find('a')
                if a_tag:
                    manufacturer = a_tag.text.strip()
                    break
                else:
                    text = elem.text.strip()
                    if "Ltd" in text or "Pvt" in text or "Pharmaceuticals" in text or "Company" in text:
                        manufacturer = text
                        break

            # 4. Price
            price_div = soup.find('span', class_='PriceBoxPlanOption__offer-price-cp___2QPU_')
            if not price_div:
                price_div = soup.find('div', class_=lambda x: x and 'DrugPriceBox__best-price___' in x)
            price = price_div.text.strip().replace('\u20b9', 'Rs. ') if price_div else ""

            # 5. Safety Advice — use pre-compiled patterns
            safety_data = {}
            for warning in soup.find_all('div', class_=RE_WARNING_TOP):
                title_node = warning.find('span')
                if title_node:
                    key = title_node.text.strip()
                    status_node = warning.parent.find('div', class_=RE_WARNING_TAG)
                    status = status_node.text.strip() if status_node else ""
                    safety_data[key] = status

            # 6. Fact Box — real class is DrugFactBox__*, extracted as key/value pairs
            fact_box_data = {}
            fact_box_section = soup.find('div', class_=RE_FACT_BOX)
            if fact_box_section:
                for row in fact_box_section.find_all('div', class_=RE_FACT_ROW):
                    key_node = row.find('div', class_=RE_FACT_KEY)
                    val_node = row.find('div', class_=RE_FACT_VAL)
                    if key_node and val_node:
                        fact_box_data[key_node.text.strip()] = val_node.text.strip()

            # 7. Drug Interactions — use pre-compiled patterns
            interactions = []
            interaction_section = soup.find('div', class_=RE_INTERACTION_WRAP)
            if interaction_section:
                panels = interaction_section.find_all('div', class_=RE_INTERACTION_PANEL)
                for p in panels:
                    drug_name = p.find('span', class_=RE_DRUG_NAME)
                    sev = p.find('span', class_=RE_SEVERITY)
                    if drug_name:
                        interactions.append(f"{drug_name.text.strip()} ({sev.text.strip() if sev else ''})")
            if not interactions:
                for h2 in soup.find_all('h2'):
                    if RE_INTERACTION_H2.search(h2.text):
                        parent_div = h2.parent
                        if parent_div:
                            next_div = parent_div.find_next_sibling('div')
                            if next_div:
                                for drug_div in next_div.find_all('div', class_=RE_DRUG_DIV):
                                    interactions.append(drug_div.text.strip())
                        break

            # Helper for text sections — uses pre-compiled patterns passed in
            def get_text_after_heading(pattern):
                for elem in soup.find_all(string=pattern):
                    parent_div = elem.parent.parent
                    if parent_div:
                        content_div = parent_div.find('div', class_=RE_DESC_CONTENT)
                        if content_div:
                            return content_div.text.strip()
                        return parent_div.text.strip()
                return ""

            # 8. Product Intro
            product_intro = get_text_after_heading(RE_PRODUCT_INTRO)

            # 9. How it works
            how_it_works = get_text_after_heading(RE_HOW_WORKS)

            # 10. Uses & Benefits
            uses = []
            benefits_text = get_text_after_heading(RE_BENEFITS_OF)

            # 11. Side Effects — use pre-compiled pattern
            side_effects = []
            overview_sections = soup.find_all('div', class_=RE_OVERVIEW_CONTENT)
            for section in overview_sections:
                heading = section.find('h2')
                heading_text = heading.text.strip().lower() if heading else ""
                if "uses of" in heading_text:
                    ul = section.find('ul')
                    if ul:
                        uses = [li.text.strip() for li in ul.find_all('li')]
                elif "side effects" in heading_text:
                    ul = section.find('ul')
                    if ul:
                        side_effects = [li.text.strip() for li in ul.find_all('li')]

            # Fallback for Uses/Side Effects
            if not uses:
                for h2 in soup.find_all('h2'):
                    if "uses of" in h2.text.strip().lower():
                        parent_div = h2.parent
                        if parent_div:
                            ul = parent_div.find('ul')
                            if not ul:
                                next_div = parent_div.find_next_sibling('div')
                                if next_div:
                                    ul = next_div.find('ul')
                            if ul:
                                uses = [li.text.strip() for li in ul.find_all('li')]
                        break
            if not side_effects:
                for h2 in soup.find_all('h2'):
                    if "side effects" in h2.text.strip().lower():
                        parent_div = h2.parent
                        if parent_div:
                            ul = parent_div.find('ul')
                            if not ul:
                                next_div = parent_div.find_next_sibling('div')
                                if next_div:
                                    ul = next_div.find('ul')
                            if ul:
                                side_effects = [li.text.strip() for li in ul.find_all('li')]
                        break

            # 12. Substitutes — use SubstituteItem__item and sub-divs for name/mfr/price
            substitutes = []
            for s in soup.find_all('div', class_=RE_SUBSTITUTE_ITEM):
                name_div  = s.find('div', class_=RE_SUB_NAME)
                mfr_div   = s.find('div', class_=RE_SUB_MFR)
                price_div_s = s.find('div', class_=RE_SUB_PRICE)
                if name_div:
                    name_text  = name_div.text.strip()
                    mfr_text   = mfr_div.text.strip()   if mfr_div   else ""
                    price_text = price_div_s.text.strip() if price_div_s else ""
                    # clean rupee symbol from price
                    price_text = price_text.replace('\u20b9', 'Rs. ')
                    substitutes.append(f"{name_text} | {mfr_text} | {price_text}")

            # 13. User Feedback — use the real style__feedback-container class
            feedback = ""
            fb_div = soup.find('div', class_=RE_USER_FEEDBACK)
            if fb_div:
                feedback = fb_div.get_text(' | ', strip=True)[:500]

            # 14. Storage
            storage = ""
            store_node = soup.find(string=RE_STORE_BELOW)
            if store_node:
                storage = store_node.strip()

            # 15. Quick Tips — find the heading text node, then walk up to the section container
            quick_tips = []
            tips_node = soup.find(string=RE_QUICK_TIPS)
            if tips_node:
                # Walk up until we find a container that has a <ul> with actual tip content
                tips_section = tips_node.parent
                for _ in range(6):  # max 6 levels up
                    if tips_section is None:
                        break
                    ul = tips_section.find('ul')
                    if ul:
                        items = [li.text.strip() for li in ul.find_all('li') if len(li.text.strip()) > 15]
                        if items:  # only accept if items look like real tips (not nav links)
                            quick_tips = items
                            break
                    tips_section = tips_section.parent

            # 16. FAQs — use real Faqs__tile/ques/ans class names
            faqs = {}
            for tile in soup.find_all('div', class_=RE_FAQ_TILE):
                q_node = tile.find('h3', class_=RE_FAQ_QUES)
                a_node = tile.find('div', class_=RE_FAQ_ANS)
                if q_node:
                    faqs[q_node.text.strip()] = a_node.text.strip() if a_node else ""

            # 17. References — use real DrugPage__reference ol tag
            references = []
            ref_ol = soup.find('ol', class_=RE_REFERENCES)
            if ref_ol:
                references = [li.text.strip() for li in ref_ol.find_all('li') if li.text.strip()]

            # 18. Marketer Details — use DrugPage__compliance-info-wrapper
            marketer_details = {}
            marketer_div = soup.find('div', class_=RE_MARKETER)
            if marketer_div:
                # Pairs of label/value divs inside the wrapper
                texts = [t.strip() for t in marketer_div.stripped_strings]
                # texts looks like: ['Name:', 'Glaxo SmithKline...', 'Address:', '...', ...]
                for i in range(0, len(texts) - 1, 2):
                    key = texts[i].rstrip(':')
                    val = texts[i + 1]
                    if key and val:
                        marketer_details[key] = val

            # 19. Prescription Required — plain string search in raw HTML (fastest)
            prescription_required = "Prescription Required" in html

            # 20. Therapeutic Class (from Fact Box)
            therapeutic_class = fact_box_data.get("Therapeutic Class", "")
            if not therapeutic_class:
                pain_node = soup.find(string=RE_PAIN)
                if pain_node:
                    therapeutic_class = pain_node.strip()

            return {
                "brand_name": brand_name,
                "composition": composition,
                "manufacturer": manufacturer,
                "price": price,
                "safety_advice": json.dumps(safety_data),
                "fact_box": json.dumps(fact_box_data),
                "drug_interactions": json.dumps(interactions),
                "product_intro": product_intro,
                "how_it_works": how_it_works,
                "uses": " | ".join(uses),
                "benefits": benefits_text,
                "side_effects": " | ".join(side_effects),
                "substitutes": json.dumps(substitutes),
                "user_feedback": feedback,
                "storage": storage,
                "quick_tips": " | ".join(quick_tips),
                "faqs": json.dumps(faqs),
                "references": json.dumps(references),
                "marketer_details": json.dumps(marketer_details),
                "prescription_required": prescription_required,
                "therapeutic_class": therapeutic_class,
                "error": ""
            }

        except Exception as e:
            print(f"Exception for {url}: {e}")
            time.sleep(2)
            
    return {"error": "Failed after 3 attempts"}

def load_urls(filename="urls.csv"):
    urls = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    urls.append(row[0])
    return list(dict.fromkeys(urls))

def load_processed_urls(output_file="medicine_details.csv"):
    processed = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("url"):
                    processed.add(row["url"])
    return processed

def process_single_url(url, writer, csvfile):
    global processed_count

    # Random jitter: prevents all threads from firing requests in synchronized bursts
    time.sleep(random.uniform(0.1, 0.5))

    result = extract_medicine_details(url)
    result["url"] = url

    # Use threading lock to prevent CSV corruption from concurrent writes
    with csv_lock:
        writer.writerow(result)
        processed_count += 1
        # Flush every 50 records to reduce disk I/O overhead
        if processed_count % 50 == 0:
            csvfile.flush()
        print(f"[{processed_count}/{total_urls}] Extracted: {url}")

def start_extraction(input_file="drugs_urls.csv", output_file="medicine_details.csv"):
    global total_urls
    global processed_count
    
    all_urls = load_urls(input_file)
    processed_urls = load_processed_urls(output_file)
    
    # Calculate exactly what is left to scrape
    urls_to_process = [u for u in all_urls if u not in processed_urls]
    
    # Setting globals for terminal print outputs
    processed_count = len(processed_urls)
    total_urls = len(all_urls)
    
    print(f"Found {len(all_urls)} total URLs.")
    print(f"Already processed: {len(processed_urls)}. Remaining to process: {len(urls_to_process)}")

    if not urls_to_process:
        print("All URLs already extracted!")
        return

    # Prepare CSV Output
    file_exists = os.path.exists(output_file)
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            "url", "brand_name", "composition", "manufacturer", "price",
            "safety_advice", "fact_box", "drug_interactions", "product_intro",
            "how_it_works", "uses", "benefits", "side_effects", "substitutes",
            "user_feedback", "storage", "quick_tips", "faqs", "references",
            "marketer_details", "prescription_required", "therapeutic_class", "error"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()

        # Execute Multi-Threaded Queue
        # 15 threads is the sweet spot for a single domain:
        # - Enough concurrency to saturate network I/O
        # - Not so many that 1mg rate-limits/throttles you (causing slow retries)
        # - Old code used 100 threads → triggered rate limiting → each retry = +6s per URL
        max_threads = 15
        print(f"Starting multi-threaded extraction using {max_threads} concurrent threads...")
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Submit all tasks to the thread pool
            futures = [executor.submit(process_single_url, url, writer, csvfile) for url in urls_to_process]
            
            # Wait for them all to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Task failed: {e}")

    print("Multi-Threaded extraction complete!")

def parse_args():
    parser = argparse.ArgumentParser(description="1mg medicine details extractor")
    parser.add_argument("--input", default="urls.csv", help="Input CSV file with URLs")
    parser.add_argument("--output", default="medicine_details.csv", help="Output CSV file for extracted data")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    start_extraction(input_file=args.input, output_file=args.output)
