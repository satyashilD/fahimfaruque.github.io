import requests


url = "https://a66c-20-124-214-182.ngrok-free.app/interactions"
data = {"drug_list": ["lisinopril","valsartan"]}

response = requests.post(url, json=data)
print(response.json())