import sys
import json
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('page.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Side effects
side_effects = []
overview_sections = soup.find_all('div', class_=lambda x: x and 'DrugOverview__content___' in x)
for section in overview_sections:
    heading = section.find('h2')
    heading_text = heading.text.strip().lower() if heading else ""
    if "side effects" in heading_text:
        ul = section.find('ul')
        if ul:
             side_effects = [li.text.strip() for li in ul.find_all('li')]

if not side_effects:
    for h2 in soup.find_all('h2'):
        if "side effects" in h2.text.strip().lower():
             parent_div = h2.parent
             if parent_div:
                 ul = parent_div.find('ul')
                 if ul:
                     side_effects = [li.text.strip() for li in ul.find_all('li')]
                 else:
                     next_div = parent_div.find_next_sibling('div')
                     if next_div:
                         ul = next_div.find('ul')
                         if ul:
                             side_effects = [li.text.strip() for li in ul.find_all('li')]
             break

if not side_effects:
    for elem in soup.find_all(string=re.compile("Side effects of ", re.I)):
        if elem.parent and elem.parent.parent:
             ul = elem.parent.parent.find('ul')
             if ul:
                  side_effects = [li.text.strip() for li in ul.find_all('li')]
                  break # to avoid matching menus


# Interactions
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
            
print("Side effects:", side_effects)
print("Interactions:", interactions)

