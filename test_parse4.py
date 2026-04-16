from bs4 import BeautifulSoup

with open("page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

title = soup.find('h1', class_='DrugHeader__title-content___2ZaPo')
brand_name = title.text.strip() if title else ""

salt_div = soup.find('div', class_='saltInfo')
composition = salt_div.text.strip() if salt_div else ""

manufacturer = ""
for elem in soup.find_all('div', class_='DrugHeader__meta-value___vqYM0'):
    a_tag = elem.find('a')
    if a_tag:
        manufacturer = a_tag.text.strip()
        break
    else:
        text = elem.text.strip()
        if "Ltd" in text or "Pvt" in text or "Pharmaceuticals" in text or "Company" in text:
            manufacturer = text
            break

print("Brand:", brand_name)
print("Composition:", composition)
print("Manufacturer:", manufacturer)

# Price
price_div = soup.find('span', class_='PriceBoxPlanOption__offer-price-cp___2QPU_')
if not price_div:
    price_div = soup.find('div', class_=lambda x: x and 'DrugPriceBox__best-price___' in x)
print("Price:", price_div.text.strip() if price_div else "N/A")

# Uses
uses = []
for use_list in soup.find_all('ul', class_=lambda x: x and 'DrugOverview__list___' in x):
    for li in use_list.find_all('li'):
        uses.append(li.text.strip())
print("Uses:", uses)
