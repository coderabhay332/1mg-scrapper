from bs4 import BeautifulSoup
import re

with open("page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Check Safety advice
print("--- Safety Advice ---")
safety_warnings = soup.find_all('div', class_=re.compile('DrugOverview__warning-top', re.I))
if not safety_warnings: # Fallback
    warnings = soup.find_all(string=re.compile('Safety advice', re.I))
    if warnings:
        parent = warnings[0].parent.parent.parent
        for div in parent.find_all('div', class_=re.compile('warning')):
            print("Warning:", div.text.strip())

for warning in soup.find_all('div', class_=re.compile('DrugOverview__warning-top')):
    title = warning.find('span')
    if title:
        print("Safety title:", title.text.strip())
        # The content usually follows in the next div or same container
        content = warning.parent.find('div', class_=re.compile('DrugOverview__content'))
        if content:
             print("Content:", content.text.strip())

print("\n--- Fact Box ---")
fact_box = soup.find('div', class_=re.compile('FactBox__fact-box'))
if not fact_box:
    fact_box_heading = soup.find(string=re.compile('Fact Box', re.I))
    if fact_box_heading:
        print(fact_box_heading.parent.parent.text)
else:
    for row in fact_box.find_all('div', class_=re.compile('FactBox__row')):
        print(row.text)

print("\n--- Drug Interactions ---")
interactions = soup.find(string=re.compile('Interaction with drugs', re.I))
if interactions:
    print(interactions.parent.parent.text[:500]) # First 500 chars

