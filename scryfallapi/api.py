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
        # Sorting the list of cards (still doesn't work)
        json_cards = sorted(json_cards_to_order, key=lambda k: ("eur" not in k, k.get("eur", None)), reverse=True)
        cards_discarded = []
        cards_not_discarded = []
        print('------------List before------------')
        for card_dict in json_cards:
            print(card_dict['name'])
            if 'eur' in card_dict.keys():
                print(card_dict['eur'])
        for card_dict in json_cards:
            if 'eur' not in card_dict.keys():
                print('Discarding this card')
                print(card_dict['name'])
                cards_discarded.append(card_dict)
            else:
                cards_not_discarded.append(card_dict)
                print('Not discarding this')
                print(card_dict['name'])
                print(card_dict['eur'])
        json_cards = cards_not_discarded + cards_discarded
        print('------------List ordered------------')
        for card_dict in json_cards:
            print(card_dict['name'])
    return json_cards
