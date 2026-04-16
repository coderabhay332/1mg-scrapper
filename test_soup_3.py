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
        if parent_div:
             print("Parent div classes:", parent_div.get('class'))
             # Let's find all text in the parent div
             # or look at children structure
             for child in parent_div.children:
                 if child.name:
                     print("-", child.name, "classes:", child.get('class'))
                     if child.name == 'div':
                         print("  Subdiv classes:", [gc.get('class') for gc in child.find_all('div') if gc.get('class')])
                     
        break
