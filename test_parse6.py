from bs4 import BeautifulSoup
import re

with open("page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

for elem in soup.find_all(string=re.compile("Uses of Dolo 650 Tablet", re.I)):
    print("Found Uses heading:", elem.parent.name, elem.parent.get('class'))
    parent_div = elem.parent.parent
    ul = parent_div.find('ul')
    if ul:
         uses = [li.text.strip() for li in ul.find_all('li')]
         print("Uses:", uses)
    else:
         print("No UL found inside parent", parent_div.name)
         # print parent_div text
         print(parent_div.text)

for elem in soup.find_all(string=re.compile("Side effects of Dolo 650 Tablet", re.I)):
    print("Found Side effects heading:", elem.parent.name, elem.parent.get('class'))
    parent_div = elem.parent.parent
    ul = parent_div.find('ul')
    if ul:
         uses = [li.text.strip() for li in ul.find_all('li')]
         print("Side effects:", uses)
