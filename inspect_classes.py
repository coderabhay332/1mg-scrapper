import requests
from bs4 import BeautifulSoup

url = "https://www.1mg.com/drugs/augmentin-625-duo-tablet-138629"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
html = requests.get(url, headers=headers).text
soup = BeautifulSoup(html, "lxml")

# Save raw HTML for inspection
with open("page_dump.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML saved ({len(html)} bytes)")

# Print all unique class names that contain key terms
keywords = ["FactBox", "DrugOverview", "Substitute", "DrugInteraction", "Quick", "Faq", "Reference", "Marketer", "User", "feedback", "how_it", "ProductDescription", "Pricing", "Price", "Drug", "Salt", "drug_"]
seen = set()
for tag in soup.find_all(True):
    classes = tag.get("class", [])
    for cls in classes:
        for kw in keywords:
            if kw.lower() in cls.lower() and cls not in seen:
                seen.add(cls)
                print(f"  <{tag.name}> class={cls}")
