from bs4 import BeautifulSoup

with open("page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

title = soup.find('h1')
print("H1 title:", title.text if title else None)

# Manufacturer typically has a class like 'manufacturer' or starts with 'Micro Labs'
# Let's find all text nodes containing 'Micro Labs'
import re
for elem in soup.find_all(text=re.compile("Micro Labs")):
    print("Found Micro Labs in tag:", elem.parent.name, "| class:", elem.parent.get('class'))

for elem in soup.find_all(text=re.compile("Paracetamol")):
    if elem.parent.name != 'script':
        print("Found Paracetamol in tag:", elem.parent.name, "| class:", elem.parent.get('class'))
