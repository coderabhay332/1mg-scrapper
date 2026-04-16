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

# Price
price_div = soup.find('span', class_='PriceBoxPlanOption__offer-price-cp___2QPU_')
if not price_div:
    price_div = soup.find('div', class_=lambda x: x and 'DrugPriceBox__best-price___' in x)
price = price_div.text.strip() if price_div else "N/A"

# Overview sections (Uses, Side Effects, etc)
overview_sections = soup.find_all('div', class_=lambda x: x and 'DrugOverview__content___' in x)
uses = []
side_effects = []
for section in overview_sections:
    heading = section.find('h2')
    heading_text = heading.text.strip().lower() if heading else ""
    if "uses of" in heading_text:
        ul = section.find('ul')
        if ul:
             uses = [li.text.strip() for li in ul.find_all('li')]
    elif "side effects" in heading_text:
        ul = section.find('ul')
        if ul:
             side_effects = [li.text.strip() for li in ul.find_all('li')]

with open('test_output.txt', 'w', encoding='utf-8') as f:
    f.write(f"Brand: {brand_name}\n")
    f.write(f"Composition: {composition}\n")
    f.write(f"Manufacturer: {manufacturer}\n")
    f.write(f"Price: {price}\n")
    f.write(f"Uses: {', '.join(uses)}\n")
    f.write(f"Side Effects: {', '.join(side_effects)}\n")
