import requests
import json

def lambda_handler(event, context):
    url = "https://78a9-20-124-214-182.ngrok-free.app/interactions"
    payload = json.dumps(event[ "drug_list"])
    headers = {
      'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    return {
        'statusCode': 200,
        'body': response.text
    }

# event = {
#       "drug_list": [
#         "aspirin",
#         "valsartan",
#         "lisinopril"
#       ]
#     }
# print(lambda_handler(event,''))