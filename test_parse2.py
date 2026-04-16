from bs4 import BeautifulSoup
import re

with open("page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
h1 = soup.find('h1')
print("Class of h1:", h1.get('class'))

# Find the div that contains manufacturer info
manufacturer_elem = soup.find(text=re.compile("Micro Labs Ltd"))
if manufacturer_elem:
    print("Manufacturer parent classes:", manufacturer_elem.parent.get('class'))
    # Let's see the parent's parent
    print("Manufacturer grandparent classes:", manufacturer_elem.parent.parent.get('class'))

# Find composition (salt) info
salt_elem = soup.find(text=re.compile("Paracetamol [\(]650mg[\)]"))
if salt_elem:
    print("Salt parent classes:", salt_elem.parent.get('class'))
else:
    for text in soup.body.stripped_strings:
        if "Paracetamol" in text and "650" in text:
            print("Found Paracetamol string:", text)

