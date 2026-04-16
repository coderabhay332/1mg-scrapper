import sys
import json
from extractor import extract_medicine_details
import requests

sys.stdout.reconfigure(encoding='utf-8')
# Dolo 650 url
url = "https://www.1mg.com/drugs/dolo-650-tablet-74467"
res = extract_medicine_details(url)
print("Side Effects:", res.get('side_effects'))
print("Drug Interactions:", res.get('drug_interactions'))
