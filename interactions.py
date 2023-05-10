import os
import requests
import openai



# Set your API key
openai.api_key = "API_KEY"

def get_drug_rxcui(drug_name):
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
    print("test")
    rxcui_list = [get_drug_rxcui(drug) for drug in drug_list]

    if None in rxcui_list:
        print("Error: One or more drug names were not recognized")
        return None

    base_url = "https://rxnav.nlm.nih.gov/REST/interaction/list.json"
    params = {"rxcuis": rxcui_list}

    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        print(f"Error: API returned status code {response.status_code}")
        return None

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Error: Unable to decode API response")
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

    if not interactions:
        print("No interactions found.")
        return

    for group in interactions:
        print(f"Interaction source: {group['sourceName']}")
        for interaction in group['fullInteractionType']:
            drug1 = interaction['minConcept'][0]['name']
            drug2 = interaction['minConcept'][1]['name']
            description = interaction['interactionPair'][0]['description']
            print(f"Interaction between {drug1} and {drug2}: {description}")

            patient_friendly_explanation = generate_patient_friendly_explanation(description)
            print(f"Patient-friendly explanation: {patient_friendly_explanation}\n")

def main():
    drug_list = input("Enter a comma-separated list of drug names: ").split(",")
    drug_list = [drug.strip() for drug in drug_list]

    interaction_data = get_drug_interactions(drug_list)
    if interaction_data is not None:
        display_interactions(interaction_data)

if __name__ == "__main__":
    main()
