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


def first_card_with_price(json_cards_to_process):
    for card in json_cards_to_process:
        if 'eur' in card.keys():
            return card
    log.error('No cards in the list with price available')
    return None


def get_most_expansive_card(name):
    response = requests.get(SCRYFALL_URL + NAMED_ENDPOINT + name)
    json_data = json.loads(response.text)
    json_cards = []
    if json_data['object'] != 'error':
        json_cards_to_process = json_data['data']
        first_card = first_card_with_price(json_cards_to_process)
        if first_card is None:
            return [], False
        json_cards.append(first_card)
        for card_dict in json_cards_to_process:
            if 'eur' in card_dict.keys():
                if float(card_dict['eur']) > float(json_cards[0]['eur']):
                    print('Exchanging ' + card_dict['name'] + ' for ' + json_cards[0]['name'])
                    json_cards[0] = card_dict
    else:
        log.error('No cards were found')
        return [], False
    if 'card_faces' in json_cards[0].keys():
        log.info('Found double-faced card')
        new_json_cards = []
        new_json_cards.append(json_cards[0]['card_faces'][0])
        new_json_cards.append(json_cards[0]['card_faces'][1])
        new_json_cards[0]['eur'], new_json_cards[1]['eur'] = json_cards[0]['eur']
        return new_json_cards, True
    return json_cards, False
