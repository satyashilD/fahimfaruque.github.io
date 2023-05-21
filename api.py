import logging
import requests
import openai
import json

import boto3

client = boto3.client('secretsmanager')

# Set your API key
#Fetch API key from AWS Secrets manager
response = client.get_secret_value(SecretId='api_key')
print(type(response))
secret = json.loads(response['SecretString'])
openai.api_key = secret['api_key']

def get_drug_rxcui(drug_name):
    print(f"fetching details of {drug_name}")
    base_url = "https://rxnav.nlm.nih.gov/REST/approximateTerm.json"
    params = {"term": drug_name}

    response = requests.get(base_url, params=params)
    data = response.json()

    candidates = data.get("approximateGroup", {}).get("candidate")

    if candidates:
        return candidates[0]["rxcui"]
    else:
        return None

def get_drug_interactions(drug_list):
    print("fetching drug rxcui")
    rxcui_list = [get_drug_rxcui(drug) for drug in drug_list]

    if None in rxcui_list:
        print("info: One or more drug names were not recognized")
        return None
    print(rxcui_list)
    base_url = "https://rxnav.nlm.nih.gov/REST/interaction/list.json"
    params = {"rxcuis": rxcui_list}

    response = requests.get(base_url, params=params)
    print(response.status_code)
    print(response.text)
    if response.status_code != 200:
        print(f"info: API returned status code {response.status_code}")
        return None

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeinfo:
        print("info: Unable to decode API response")
        return None

    return data

def generate_patient_friendly_explanation(text):
    prompt = f"Explain the following drug interaction in patient-friendly language: {text}"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].text.strip()

def display_interactions(interaction_data):
    interactions = interaction_data.get("fullInteractionTypeGroup")
    result = dict()
    if not interactions:
        print("No interactions found.")
        return

    for group in interactions:
        print(f"Interaction source: {group['sourceName']}")
        for interaction in group['fullInteractionType']:
            drug1 = interaction['minConcept'][0]['name']
            drug2 = interaction['minConcept'][1]['name']
            description = interaction['interactionPair'][0]['description']
            msg = f"Interaction between {drug1} and {drug2}: {description}"
            print(msg)

            patient_friendly_explanation = generate_patient_friendly_explanation(description)
            print(f"Patient-friendly explanation: {patient_friendly_explanation}\n")
            return patient_friendly_explanation


def lambda_handler(event, context):
    print(event)
    try:
        print("inside try")
        data = json.loads(event['body'])
        print("json dump", type(data))
        drug1 = data['drug1']
        drug2 = data['drug2']
        print(f"Reveived drug names are {drug1}, {drug2}")
        drug_list = [drug1, drug2]
        interaction_data = get_drug_interactions(drug_list)
        if interaction_data is not None:
            response = display_interactions(interaction_data)
            return {'statusCode': 200,'body': response}
        else:
            return {'statusCode': 502,'body': 'Unable to retrieve drug interactions'}
    except Exception as e:
        return {
        'statusCode': 502,
        'body': 'An unexpected info occurred'
    }
