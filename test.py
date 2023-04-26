import requests


url = "https://dbe0-20-124-214-182.ngrok-free.app/interaction"
data = {"drug_list": [drug1,drug2]}

response = requests.post(url, json=data)
print(response.json())