import json

import requests

import logger

SCRYFALL_URL = 'https://api.scryfall.com'
RANDOM_ENDPOINT = '/cards/random'
NAMED_ENDPOINT = '/cards/search?order=released&q='

log = logger.get_logger()


def get_random_card():
    response = requests.get(SCRYFALL_URL + RANDOM_ENDPOINT)
    json_card = json.loads(response.text)
    print(json_card.keys())
    return json_card


def get_named_card(name):
    response = requests.get(SCRYFALL_URL + NAMED_ENDPOINT + name)
    json_data = json.loads(response.text)
    json_cards = []
    if json_data['object'] != 'error':
        json_cards_to_order = json_data['data']
        # Sorting the list of cards
        json_cards = sorted(json_cards_to_order, key=lambda k: ("eur" not in k, k.get("eur", None)), reverse=True)
        i = 0
        print(json_cards)
        for card_dict in json_cards:
            print('processing')
            print(card_dict['name'])
            if 'eur' not in card_dict.keys():
                print('This card moved to last position')
                print(card_dict['name'])
                json_cards.pop(i)
                print(json_cards)
            else:
                i += 1
        print(json_cards)
    return json_cards
