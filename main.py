from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import csv

def scrape_medicine_data(url):
    with sync_playwright() as p:
        # Launch browser (set headless=False if you want to watch it work)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Anti-bot tactic: Set a realistic user agent
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        })

        try:
            page.goto(url)
            # Crucial: Wait for the specific element that holds the drug info to load
            # You will need to inspect 1mg's DOM to get the exact class names
            page.wait_for_selector('h1.DrugHeader__title-content___2ZaPo', timeout=10000) 
            
            # Get the fully rendered HTML
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Example extraction (You must adjust these class names based on 1mg's current DOM)
            brand_name = soup.find('h1', class_='DrugHeader__title-content___2ZaPo').text.strip()
            composition = soup.find('div', class_='saltInfo').text.strip()
            
            print(f"Brand: {brand_name} | Generic: {composition}")
            
            return {"brand": brand_name, "generic": composition}

        except Exception as e:
            print(f"Error scraping {url}: {e}")
        finally:
            browser.close()

# Example usage
url = "https://www.1mg.com/drugs/dolo-650-tablet-74467"
scrape_medicine_data(url)