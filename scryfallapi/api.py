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


def get_list_card_by_name(name):
    response = requests.get(SCRYFALL_URL + NAMED_ENDPOINT + name)
    json_data = json.loads(response.text)
    json_cards = []
    if json_data['object'] != 'error':
        for card in json_data['data']:
            json_cards.append(card)
    else:
        log.error('No cards were found')
        return []
    return json_cards


def get_specific_card(name):
    response = requests.get(SCRYFALL_URL + NAMED_ENDPOINT + name)
    json_data = json.loads(response.text)
    if json_data['object'] != 'error':
        return json_data['data'][0]
    else:
        log.error('No cards were found')
        return []
    return json_cards


def first_card_with_price(json_cards_to_process):
    for card in json_cards_to_process:
        if card['prices']['eur'] is not None:
            return card
    log.error('No cards in the list with price available')
    return None


# TODO: make more simple to way to get the most expansive card
def get_most_expansive_card(name):
    response = requests.get(SCRYFALL_URL + NAMED_ENDPOINT + name)
    json_data = json.loads(response.text)
    json_cards = []
    if json_data['object'] != 'error':
        json_cards_to_process = json_data['data']
        first_card = first_card_with_price(json_cards_to_process)
        if first_card is None:
            return []
        json_cards.append(first_card)
        for card_dict in json_cards_to_process:
            if card_dict['prices']['eur'] is not None:
                if float(card_dict['prices']['eur']) > float(json_cards[0]['prices']['eur']):
                    print('Exchanging ' + card_dict['name'] + ' for ' + json_cards[0]['name'])
                    json_cards[0] = card_dict
    else:
        log.error('No cards were found')
        return []
    return json_cards
