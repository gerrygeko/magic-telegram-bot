import json
import requests
from urllib.parse import urlencode

import logger

SCRYFALL_URL = 'https://api.scryfall.com'
RANDOM_ENDPOINT = '/cards/random'
NAMED_ENDPOINT = '/cards/search?order=released&q='

log = logger.get_logger()


def get_random_card():
    response = requests.get(SCRYFALL_URL + RANDOM_ENDPOINT)
    json_data = json.loads(response.text)
    print(json_data)
    return json_data


def get_named_card(name):
    response = requests.get(SCRYFALL_URL + NAMED_ENDPOINT + name)
    json_data = json.loads(response.text)
    return json_data
