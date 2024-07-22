import requests
from config import ALPHA_API_KEY

url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=ETH&to_currency=EUR&apikey={ALPHA_API_KEY}'
r = requests.get(url)
data = r.json()

print(data)
