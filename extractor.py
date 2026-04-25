import csv
import time
import os
import requests
from bs4 import BeautifulSoup
import re
import json
import threading
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Thread lock to prevent multiple threads from writing to the CSV at the exact same microsecond
csv_lock = threading.Lock()
processed_count = 0
total_urls = 0

def extract_medicine_details(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"HTTP {response.status_code} for {url}. Retrying...")
                time.sleep(2)
                continue
            
            html = response.text
            soup = BeautifulSoup(html, "html.parser")

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

            # 5. Safety Advice
            safety_data = {}
            for warning in soup.find_all('div', class_=re.compile('DrugOverview__warning-top')):
                title_node = warning.find('span')
                if title_node:
                    key = title_node.text.strip()
                    status_node = warning.parent.find('div', class_=re.compile('DrugOverview__warning-tag'))
                    status = status_node.text.strip() if status_node else ""
                    safety_data[key] = status
            
            # 6. Fact Box
            fact_box_data = {}
            fact_box_section = soup.find('div', class_=re.compile('FactBox__fact-box'))
            if fact_box_section:
                for row in fact_box_section.find_all('div', class_=re.compile('FactBox__row')):
                    key_node = row.find('div', class_=re.compile('FactBox__key'))
                    val_node = row.find('div', class_=re.compile('FactBox__value'))
                    if key_node and val_node:
                        fact_box_data[key_node.text.strip()] = val_node.text.strip()

            # 7. Drug Interactions
            interactions = []
            interaction_section = soup.find('div', class_=re.compile('DrugInteraction__drug-interaction-wrapper'))
            if interaction_section:
                 panels = interaction_section.find_all('div', class_=re.compile('DrugInteraction__interaction-panel'))
                 for p in panels:
                     drug_name = p.find('span', class_=re.compile('DrugInteraction__drug-name'))
                     sev = p.find('span', class_=re.compile('DrugInteraction__severity-text'))
                     if drug_name:
                         interactions.append(f"{drug_name.text.strip()} ({sev.text.strip() if sev else ''})")
            if not interactions:
                for h2 in soup.find_all('h2'):
                    if "interaction" in h2.text.strip().lower():
                        parent_div = h2.parent
                        if parent_div:
                            next_div = parent_div.find_next_sibling('div')
                            if next_div:
                                for drug_div in next_div.find_all('div', class_=lambda x: x and 'DrugInteraction__drug___' in x):
                                    interactions.append(drug_div.text.strip())
                        break

            # Helper for text sections
            def get_text_after_heading(heading_regex):
                for elem in soup.find_all(string=re.compile(heading_regex, re.I)):
                    parent_div = elem.parent.parent
                    if parent_div:
                        content_div = parent_div.find('div', class_=re.compile("ProductDescription__description-content", re.I))
                        if content_div:
                            return content_div.text.strip()
                        return parent_div.text.strip()
                return ""
            
            # 8. Product Intro
            product_intro = get_text_after_heading('Product introduction')

            # 9. How it works
            how_it_works = get_text_after_heading('How .* works')

            # 10. Uses & Benefits
            uses = []
            benefits_text = get_text_after_heading('Benefits of')
            
            # 11. Side Effects
            side_effects = []
            overview_sections = soup.find_all('div', class_=lambda x: x and 'DrugOverview__content___' in x)
            for section in overview_sections:
                heading = section.find('h2')
                heading_text = heading.text.strip().lower() if heading else ""
                if "uses of" in heading_text:
                    ul = section.find('ul')
                    if ul: uses = [li.text.strip() for li in ul.find_all('li')]
                elif "side effects" in heading_text:
                    ul = section.find('ul')
                    if ul: side_effects = [li.text.strip() for li in ul.find_all('li')]
            
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

            # 12. Substitutes
            substitutes = []
            subs_node = soup.find(string=re.compile('All substitutes', re.I))
            if subs_node and subs_node.parent and subs_node.parent.parent and subs_node.parent.parent.parent:
                subs_container = subs_node.parent.parent.parent
                for s in subs_container.find_all('div', class_=re.compile('SubstituteItem')):
                    substitutes.append(s.text.strip())

            # 13. User Feedback
            feedback = ""
            feedback_node = soup.find(string=re.compile('User feedback', re.I))
            if feedback_node and feedback_node.parent and feedback_node.parent.parent and feedback_node.parent.parent.parent:
                container = feedback_node.parent.parent.parent
                feedback = container.text.strip()

            # 14. Storage
            storage = ""
            store_node = soup.find(string=re.compile('Store below', re.I))
            if store_node:
                storage = store_node.strip()

            # 15. Quick Tips
            quick_tips = []
            tips_section = soup.find('div', string=re.compile('Quick tips', re.I))
            if tips_section:
                ul = tips_section.find_next('ul')
                if ul:
                    quick_tips = [li.text.strip() for li in ul.find_all('li')]

            # 16. FAQs
            faqs = {}
            faq_headings = soup.find_all('h3')
            for h3 in faq_headings:
                question = h3.text.strip()
                if question:
                    answer_div = h3.find_next('p')
                    if answer_div:
                        faqs[question] = answer_div.text.strip()

            # 17. References
            references = []
            ref_node = soup.find(string=re.compile('References', re.I))
            if ref_node:
                parent = ref_node.parent
                if parent:
                    ul = parent.find('ul')
                    if ul:
                        references = [li.text.strip() for li in ul.find_all('li')]

            # 18. Marketer Details
            marketer_details = {}
            marketer_node = soup.find(string=re.compile('Marketer details', re.I))
            if marketer_node:
                parent_div = marketer_node.parent.parent
                if parent_div:
                    for row in parent_div.find_all('div', class_=re.compile('row')):
                        key_node = row.find('div', class_=re.compile('key'))
                        val_node = row.find('div', class_=re.compile('value'))
                        if key_node and val_node:
                            marketer_details[key_node.text.strip()] = val_node.text.strip()

            # 19. Prescription Required
            prescription_required = "Prescription Required" in html

            # 20. Therapeutic Class (from Fact Box)
            therapeutic_class = ""
            pain_node = soup.find(string=re.compile('PAIN ANALGESICS', re.I))
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
    
    result = extract_medicine_details(url)
    result["url"] = url
    
    # Use threading lock to prevent CSV corruption from concurrent writes
    with csv_lock:
        writer.writerow(result)
        csvfile.flush()
        processed_count += 1
        print(f"[{processed_count}/{total_urls}] Extracted: {url}")
        
    time.sleep(1) # Small 1s delay per thread as a precaution

def start_extraction(input_file="urls.csv", output_file="medicine_details.csv"):
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
        # We start with 5 threads. This runs 5 simultaneous jobs.
        max_threads = 100
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
