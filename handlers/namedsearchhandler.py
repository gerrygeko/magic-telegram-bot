from telegram import InputMediaPhoto, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, Filters, CommandHandler

import logger
import telegramutils
from scryfallapi import api

START, CHOOSING, PICKING, = range(3)
log = logger.get_logger()
fallback = []


def search(bot, update):
    telegramutils.send_text_message(bot, update,
                                    "Type the name of the card you want to search. It doesn't need to be the exact "
                                    "name. The most expansive one will be showed")
    return CHOOSING


def get_named_cards(bot, update):
    card_name = update.message.text
    log.info('User is searching for cards that contain in the text name the word: %s', card_name)
    most_expansive_card_list, double_faced = api.get_most_expansive_card(card_name)
    card_list_by_name = api.get_list_card_by_name(card_name)
    if len(most_expansive_card_list) == 0:
        telegramutils.send_text_message(bot, update, "No cards found with the text that you typed, type a new name")
        return CHOOSING
    else:
        if not double_faced:
            telegramutils.send_picture(bot, update, most_expansive_card_list[0])
        else:
            media = create_media_group_for_double_faced_cards(most_expansive_card_list)
            telegramutils.send_message_with_media_group(bot, update, media)
        telegramutils.send_message_with_card_cost(bot, update, most_expansive_card_list[0])
        if len(card_list_by_name) > 0:
            telegramutils.send_message_with_keyboard(bot, update, create_keyboard_from_card_list(card_list_by_name),
                                                     "Other cards that also contains the text you provided: ",
                                                     one_time_use=True)
            return PICKING
        return START


def get_specific_card(bot, update):
    card_name = update.message.text
    log.info('User is searching for the specific card %s', card_name)
    card = api.get_specific_card(card_name)
    telegramutils.send_picture(bot, update, card)
    telegramutils.send_message_with_card_cost(bot, update, card, True)
    return START


def search_interrupted(bot, update):
    telegramutils.send_text_message(bot, update, "Search interrupted.")


# Method to create a media group to display more images if the card is composed by more
def create_media_group_for_double_faced_cards(card_list):
    media = []
    media_one = InputMediaPhoto(media=card_list[0]['image_uris']['normal'])
    media_two = InputMediaPhoto(media=card_list[1]['image_uris']['normal'])
    media.append(media_one)
    media.append(media_two)
    return media


def create_keyboard_from_card_list(card_list):
    keyboard = []
    row = None
    first_element = True
    for i in range(0, len(card_list)):
        if first_element:
            row = [KeyboardButton(text=card_list[i]['name'])]
            first_element = False
        else:
            row.append(KeyboardButton(text=card_list[i]['name']))
            keyboard.append(row)
            first_element = True
    return keyboard


states = {
    START: [CommandHandler('search', search)],
    CHOOSING: [MessageHandler(Filters.text, get_named_cards)],
    PICKING: [MessageHandler(Filters.text, get_specific_card)],
}


class NamedSearchHandler(ConversationHandler):

    def __init__(self,
                 allow_reentry=False,
                 run_async_timeout=None,
                 timed_out_behavior=None,
                 per_chat=True,
                 per_user=True,
                 per_message=False,
                 conversation_timeout=None):
        self.states = states
        self.entry_points = [CommandHandler('search', search)]
        self.fallbacks = fallback
        self.allow_reentry = allow_reentry
        self.run_async_timeout = run_async_timeout
        self.timed_out_behavior = timed_out_behavior
        self.per_user = per_user
        self.per_chat = per_chat
        self.per_message = per_message
        self.conversation_timeout = conversation_timeout
        self.timeout_jobs = dict()
        self.conversations = dict()
        self.current_conversation = None
        self.current_handler = None
        self.logger = log
