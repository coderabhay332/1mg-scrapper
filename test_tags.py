import requests
from bs4 import BeautifulSoup

url = "https://www.1mg.com/drugs/augmentin-625-duo-tablet-138629"
headers = {"User-Agent": "Mozilla/5.0"}
html = requests.get(url, headers=headers).text
soup = BeautifulSoup(html, "lxml")

for tag in soup.find_all(['h2', 'h3']):
    print(tag.name, tag.text.strip())
