import sys
import json
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('page.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("All h2 tags:")
for h2 in soup.find_all('h2'):
    print(h2.text.strip())

print("---")
side_effects = []
overview_sections = soup.find_all('div', class_=lambda x: x and 'DrugOverview__content___' in x)
for section in overview_sections:
    heading = section.find('h2')
    heading_text = heading.text.strip().lower() if heading else ""
    if "side effects" in heading_text:
        ul = section.find('ul')
        if ul: side_effects = [li.text.strip() for li in ul.find_all('li')]

if not side_effects:
    for elem in soup.find_all(string=re.compile("Side effects of ", re.I)):
        if elem.parent and elem.parent.parent:
             ul = elem.parent.parent.find('ul')
             if ul:
                  side_effects = [li.text.strip() for li in ul.find_all('li')]

interactions = []
interaction_section = soup.find('div', class_=re.compile('DrugInteraction__drug-interaction-wrapper'))
if interaction_section:
     panels = interaction_section.find_all('div', class_=re.compile('DrugInteraction__interaction-panel'))
     for p in panels:
         drug_name = p.find('span', class_=re.compile('DrugInteraction__drug-name'))
         sev = p.find('span', class_=re.compile('DrugInteraction__severity-text'))
         if drug_name:
             interactions.append(f"{drug_name.text.strip()} ({sev.text.strip() if sev else ''})")

print("Side effects:", side_effects)
print("Interactions class DrugInteraction__drug-interaction-wrapper exists?", interaction_section is not None)
print("Interactions:", interactions)

