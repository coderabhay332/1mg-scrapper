import sys
import json
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('page.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

side_effects = []
for h2 in soup.find_all('h2'):
    if "side effects" in h2.text.strip().lower():
        parent_div = h2.parent
        print("Side effect parent div classes:")
        if parent_div:
             print(parent_div.get('class'))
             # get text next to it or ul inside it?
             ul = parent_div.find('ul')
             if ul:
                print("Found ul in same parent div as h2.")
                side_effects = [li.text.strip() for li in ul.find_all('li')]
             else:
                next_div = h2.find_next_sibling('div')
                if next_div:
                    print("Found sibling div for h2:")
                    print(next_div.text[:100] + "...")
        break
        
print("Extracted Side effects:", side_effects)

print("---")
interactions = []
for h2 in soup.find_all('h2'):
    if "interaction with drugs" in h2.text.strip().lower():
        parent_div = h2.parent
        if parent_div:
             # Look for specific children with drug names
             # The new website might just have a div list
             interactions_div = parent_div.find_next_sibling('div') or parent_div
             text = parent_div.text
             print("Interactions block text snippet:", text[:200])
             # Let's find elements that look like drugs with severity
             # Usually there are spans/divs with interaction names
             
        break
