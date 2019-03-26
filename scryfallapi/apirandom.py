import json
import requests

SCRYFALL_URL = 'https://api.scryfall.com'
RANDOM_ENDPOINT = '/cards/random'

def get_random_card():
    response = requests.get(SCRYFALL_URL + RANDOM_ENDPOINT)
    json_data = json.loads(response.text)
    print(json_data)
    return json_data
