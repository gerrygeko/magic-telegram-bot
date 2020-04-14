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
    return json_card


def get_list_card_by_name(name):
    response = requests.get(SCRYFALL_URL + NAMED_ENDPOINT + name)
    json_data = json.loads(response.text)
    if json_data['object'] == 'error':
        log.error('No cards were found')
        return None
    else:
        return json_data['data']


def get_list_card_for_reprints(uri):
    response = requests.get(uri)
    json_data = json.loads(response.text)
    if json_data['object'] == 'error':
        log.error('No reprints were found')
        return None
    else:
        return json_data['data']


def get_specific_card(name):
    response = requests.get(SCRYFALL_URL + NAMED_ENDPOINT + name)
    json_data = json.loads(response.text)
    if json_data['object'] != 'error':
        return json_data['data'][0]
    else:
        log.error('No cards were found')
        return None


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
    if json_data['object'] != 'error':
        json_cards_to_process = json_data['data']
        expensive_card = max(json_cards_to_process,
                             key=lambda card: (float(card['prices']['eur']) if card['prices']['eur'] is not None else 0))
        return expensive_card
    else:
        log.error('No cards were found')
        return None
