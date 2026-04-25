from bs4 import BeautifulSoup
import re

with open("page_dump.html", "r", encoding="utf-8") as f:
    html = f.read()
soup = BeautifulSoup(html, "lxml")

print("=== FACT BOX ===")
fb = soup.find("div", class_=re.compile("DrugFactBox__content"))
if fb:
    print(fb.get_text(" | ", strip=True)[:300])

print("\n=== SUBSTITUTES (first 3) ===")
for s in soup.find_all("div", class_=re.compile("SubstituteItem__item"))[:3]:
    name = s.find("div", class_=re.compile("SubstituteItem__name"))
    mfr  = s.find("div", class_=re.compile("SubstituteItem__manufacturer"))
    price= s.find("div", class_=re.compile("SubstituteItem__price"))
    print(f"  {name and name.text.strip()} | {mfr and mfr.text.strip()} | {price and price.text.strip()}")

print("\n=== QUICK TIPS ===")
# Find the section with "Quick tips" heading
for div in soup.find_all("div"):
    txt = div.get_text()
    if "Quick tips" in txt and "Take Augmentin" in txt:
        ul = div.find("ul")
        if ul:
            for li in ul.find_all("li"):
                print(" -", li.text.strip()[:80])
        break

print("\n=== FAQs ===")
faq_tiles = soup.find_all("div", class_=re.compile("Faqs__tile"))
for tile in faq_tiles[:3]:
    q = tile.find("h3", class_=re.compile("Faqs__ques"))
    a = tile.find("div", class_=re.compile("Faqs__ans"))
    if q:
        print(f"  Q: {q.text.strip()[:80]}")
        if a: print(f"  A: {a.text.strip()[:100]}")

print("\n=== HOW IT WORKS ===")
for h2 in soup.find_all("h2"):
    if "works" in h2.text.lower():
        container = h2.find_parent("div")
        if container:
            p = container.find("p") or container.find("div", class_=re.compile("DrugOverview__content"))
            if p: print(p.text.strip()[:300])
        break

print("\n=== REFERENCES ===")
ref_ol = soup.find("ol", class_=re.compile("DrugPage__reference"))
if ref_ol:
    for li in ref_ol.find_all("li")[:3]:
        print(" -", li.text.strip()[:120])

print("\n=== MARKETER DETAILS ===")
# Look for marketer section in compliance-info
comp = soup.find("div", class_=re.compile("DrugPage__compliance-info-wrapper"))
if comp:
    print(comp.get_text(" | ", strip=True)[:400])

print("\n=== USER FEEDBACK ===")
fb_div = soup.find("div", class_=re.compile("style__feedback-container"))
if fb_div:
    print(fb_div.get_text(" | ", strip=True)[:300])
