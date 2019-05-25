import requests
import json


test = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=5min&outputsize=full&apikey=demo")
data = json.loads(test.text)
print(data)
print(type(test))
print(test)