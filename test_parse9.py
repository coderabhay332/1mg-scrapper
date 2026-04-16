import requests
from bs4 import BeautifulSoup
import re
import json

with open("page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

def get_text_after_heading(heading_regex):
    for elem in soup.find_all(string=re.compile(heading_regex, re.I)):
        parent_div = elem.parent.parent
        if parent_div:
            # check if it's the heading we want
            text = parent_div.text.strip()
            # typically the content is the next sibling or inside the next div
            # let's just get the text of the container that comes after the heading container
            content_div = parent_div.find('div', class_=re.compile("ProductDescription__description-content", re.I))
            if content_div:
                return content_div.text.strip()
            # or it might be in the same overview block
            return parent_div.text.strip()
    return ""

product_intro = get_text_after_heading('Product introduction')
how_it_works = get_text_after_heading('How .* works')
uses = get_text_after_heading('Uses of')
benefits = get_text_after_heading('Benefits of')

# Substitutes
substitutes = []
subs_node = soup.find('div', class_=re.compile('SubstituteList'))
if not subs_node:
    subs_node = soup.find(string=re.compile('All substitutes', re.I))
    if subs_node:
        print("Found substitutes heading")
        subs_container = subs_node.parent.parent.parent
        for s in subs_container.find_all('div', class_=re.compile('SubstituteItem')):
            substitutes.append(s.text.strip())

# User feedback
feedback = []
feedback_node = soup.find(string=re.compile('User feedback', re.I))
if feedback_node:
    container = feedback_node.parent.parent.parent
    feedback = container.text.strip()[:200]

print(json.dumps({
    "product_intro": product_intro[:100],
    "how_it_works": how_it_works[:100],
    "uses": uses[:100],
    "benefits": benefits[:100],
    "substitutes": substitutes,
    "feedback": feedback
}, indent=2))
