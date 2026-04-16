import requests
from bs4 import BeautifulSoup

url = "https://www.1mg.com/drugs/dolo-650-tablet-74467"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}
try:
    response = requests.get(url, headers=headers, timeout=10)
    print("Status code:", response.status_code)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find('h1', class_='DrugHeader__title-content___2ZaPo')
        print("Title with requests:", title.text if title else "Not found")
except Exception as e:
    print("Failed", e)
