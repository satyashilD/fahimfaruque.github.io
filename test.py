import requests


url = "https://e3a4-20-124-214-182.ngrok-free.app/interactions"
data = {"drug_list": ["aspirin","valsartan","lisinopril"]}

response = requests.post(url, json=data)
print(response.json())