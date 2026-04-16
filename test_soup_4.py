import sys
import json
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('page.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("--- Interactions ---")
for h2 in soup.find_all('h2'):
    if "interaction" in h2.text.strip().lower():
        parent_div = h2.parent
        next_div = parent_div.find_next_sibling('div')
        if next_div:
            print("Next div classes:", next_div.get('class'))
            for p in next_div.find_all('div'):
                 classes = p.get('class')
                 if classes and 'Interaction' in str(classes):
                      print("Found child div with classes:", classes)
                 # Wait, let's just print the text of the next div
                 
            # If the class name is not DrugInteraction, what is it?
            print("Classes inside next_div that might contain the data:")
            for d in next_div.find_all('div'):
                  if d.get('class') and len(d.text.strip()) > 0 and len(d.text.strip()) < 50:
                       print("Class:", d.get('class'), "Text:", d.text.strip())

        break
