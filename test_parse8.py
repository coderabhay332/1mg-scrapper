import requests
from bs4 import BeautifulSoup
import re
import json

url = "https://www.1mg.com/drugs/avastin-100mg-injection-269389"
headers = {"User-Agent": "Mozilla/5.0"}
try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 1. Title/Brand
        title = soup.find('h1', class_='DrugHeader__title-content___2ZaPo')
        brand_name = title.text.strip() if title else ""
        
        # 2. Salt/Composition
        salt_div = soup.find('div', class_='saltInfo')
        composition = salt_div.text.strip() if salt_div else ""
        
        # 3. Safety Warning tags
        safety_data = {}
        for warning in soup.find_all('div', class_=re.compile('DrugOverview__warning-top')):
            title_node = warning.find('span')
            if title_node:
                key = title_node.text.strip()
                # Status (e.g., UNSAFE, CONSULT YOUR DOCTOR)
                status_node = warning.parent.find('div', class_=re.compile('DrugOverview__warning-tag'))
                status = status_node.text.strip() if status_node else ""
                
                safety_data[key] = status
        
        # 4. Fact Box (classes)
        fact_box_data = {}
        fact_box_section = soup.find('div', class_=re.compile('FactBox__fact-box'))
        if fact_box_section:
            for row in fact_box_section.find_all('div', class_=re.compile('FactBox__row')):
                key_node = row.find('div', class_=re.compile('FactBox__key'))
                val_node = row.find('div', class_=re.compile('FactBox__value'))
                if key_node and val_node:
                    fact_box_data[key_node.text.strip()] = val_node.text.strip()

        # 5. Interactions
        interactions = []
        interaction_section = soup.find('div', class_=re.compile('DrugInteraction__drug-interaction-wrapper'))
        if interaction_section:
             panels = interaction_section.find_all('div', class_=re.compile('DrugInteraction__interaction-panel'))
             for p in panels:
                 drug_name = p.find('span', class_=re.compile('DrugInteraction__drug-name'))
                 sev = p.find('span', class_=re.compile('DrugInteraction__severity-text'))
                 if drug_name:
                     interactions.append(f"{drug_name.text.strip()} ({sev.text.strip() if sev else ''})")

        print(json.dumps({
            "brand_name": brand_name,
            "composition": composition,
            "safety_data": safety_data,
            "fact_box_data": fact_box_data,
            "interactions": interactions
        }, indent=2))
except Exception as e:
    print(e)

