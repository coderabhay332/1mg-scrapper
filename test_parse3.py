from bs4 import BeautifulSoup
import re

with open("page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
h1 = soup.find('h1', class_='DrugHeader__title-content___2ZaPo')
print("Title:", h1.text if h1 else None)

# Manufacturer
manufacturer_node = soup.find(string=re.compile("Manufacturer"))
if manufacturer_node and manufacturer_node.parent:
    grandparent = manufacturer_node.parent.parent
    if grandparent:
        value_node = grandparent.find('a')
        print("Manufacturer:", value_node.text.strip() if value_node else None)

# Salt / Composition
salt_div = soup.find('div', class_='saltInfo')
if salt_div:
    print("Salt/Composition (saltInfo class):", salt_div.text.strip())
else:
    # Alternative: check for text "Composition" or similar
    salt_header = soup.find('div', class_=re.compile("saltInfo", re.I))
    if salt_header:
         print("Found saltInfo case insensitive:", salt_header)
    for a in soup.find_all('a'):
        href = a.get('href', '')
        if '/medicines/' in href and not '/drugs/' in href:
            pass # Maybe not
    # See if there's drug composition in DrugHeader
    header_salt = soup.find('div', class_='saltInfo')

    # Look around DrugHeader
    header = soup.find('div', class_=re.compile("DrugHeader"))
    if header:
         print("\n--- DrugHeader text ---")
         print(header.text)
