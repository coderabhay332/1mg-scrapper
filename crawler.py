import csv
import string
import time
import json
import os
import requests
from bs4 import BeautifulSoup
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

state_lock = threading.Lock()
csv_lock = threading.Lock()

def load_state(state_file):
    default_state = {letter: 1 for letter in string.ascii_lowercase}
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            try:
                old_state = json.load(f)
                # Check if it's the old format
                if 'letter' in old_state and 'page' in old_state:
                    resume_letter = old_state['letter']
                    resume_page = old_state['page']
                    # Convert to new format
                    for l in string.ascii_lowercase:
                        if l < resume_letter:
                            default_state[l] = 'done'
                        elif l == resume_letter:
                            default_state[l] = resume_page
                        else:
                            default_state[l] = 1
                    # Save the new format back immediately
                    save_state(state_file, default_state)
                    return default_state
                else:
                    # Assume new format
                    for l in string.ascii_lowercase:
                        if l in old_state:
                            default_state[l] = old_state[l]
                    return default_state
            except Exception as e:
                print(f"Error loading state: {e}. Starting fresh.")
                pass
    return default_state

def save_state(state_file, state):
    with state_lock:
        with open(state_file, 'w') as f:
            json.dump(state, f)

def crawl_letter(letter, start_page, state, state_file, output_file, max_pages=500):
    base_url = "https://www.1mg.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    print(f"--- Starting thread for '{letter.upper()}' from page {start_page} ---")
    
    for page_num in range(start_page, max_pages + 1):
        url = f"{base_url}/drugs-all-medicines?label={letter}&page={page_num}"
        success = False
        urls_found = []
        
        for attempt in range(3):
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code != 200:
                    print(f"[{letter.upper()}] HTTP {resp.status_code} on page {page_num}. Retrying...")
                    time.sleep(2)
                    continue
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                drug_links = soup.find_all('a', href=True)
                for node in drug_links:
                    href = node.get('href')
                    if href and '/drugs/' in href and not '?' in href:
                        full_url = base_url + href
                        urls_found.append(full_url)
                
                urls_found = list(set(urls_found))
                success = True
                break
            except Exception as e:
                print(f"[{letter.upper()}] Attempt {attempt + 1} failed for {url}: {e}")
                time.sleep(3)
                
        if not success:
            print(f"[{letter.upper()}] Skipping page {page_num} after 3 failed attempts.")
            break # Break letter loop on total failure to avoid skipping gaps, manual resume can handle it
            
        if not urls_found:
            print(f"[{letter.upper()}] No URLs found on page {page_num}. Ending letter.")
            # Mark letter as finished
            with state_lock:
                state[letter] = 'done'
            save_state(state_file, state)
            break
            
        # Save to CSV
        with csv_lock:
            with open(output_file, mode='a', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                for u in urls_found:
                    writer.writerow([u])
                    
        print(f"[{letter.upper()}] Saved {len(urls_found)} URLs from page {page_num}")
        
        # Update State
        with state_lock:
            state[letter] = page_num + 1
        save_state(state_file, state)
        
        time.sleep(1) # slight delay to prevent hammering the server

def crawl_1mg_urls(output_file="urls.csv", state_file="crawler_state.json", max_pages_per_letter=500):
    state = load_state(state_file)
    
    # Check which letters still need crawling
    letters_to_crawl = []
    for letter in string.ascii_lowercase:
        val = state.get(letter)
        if val != 'done':
            # It could be an integer page number
            start_page = int(val) if val else 1
            letters_to_crawl.append((letter, start_page))
            
    if not letters_to_crawl:
        print("All letters have been fully crawled!")
        return
        
    print(f"Resuming/Starting crawl for {len(letters_to_crawl)} letters...")
    
    # Using 10 workers ensures good concurrency without instantly getting blocked due to rate limits
    max_workers = min(10, len(letters_to_crawl)) 
    print(f"Starting multi-threaded extraction using {max_workers} concurrent threads...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(crawl_letter, letter, start_page, state, state_file, output_file, max_pages_per_letter)
            for letter, start_page in letters_to_crawl
        ]
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Thread failed: {e}")
                
    print(f"Done crawling! URLs are saved in {output_file}")

if __name__ == "__main__":
    crawl_1mg_urls()
