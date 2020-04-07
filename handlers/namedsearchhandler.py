from telegram import InputMediaPhoto, KeyboardButton
from telegram.ext import ConversationHandler, MessageHandler, Filters, CommandHandler

import logger
import telegramutils
from scryfallapi import api, bot_state

states = bot_state.NamedSearchStates
log = logger.get_logger()
fallback = []


def search_command(bot, update):
    log.info('User %s is in the suggestion phase', telegramutils.get_user_from_update(update))
    telegramutils.send_text_message(bot, update,
                                    "Type the name of the card you want to search. It doesn't need to be the exact "
                                    "name. The most expansive one will be showed. "
                                    "You can abort at any moment the search by executing the /abort command")
    return states.CHOOSING


def get_named_cards(bot, update):
    card_name = update.message.text
    log.info('User %s is searching for cards that contain in the text name the word: %s',
             telegramutils.get_user_from_update(update), card_name)
    most_expansive_card_list = api.get_most_expansive_card(card_name)
    card_list_by_name = api.get_list_card_by_name(card_name)
    if len(most_expansive_card_list) == 0:
        telegramutils.send_text_message(bot, update, "No cards found with the text that you typed, type a new name")
        return states.CHOOSING
    else:
        telegramutils.send_picture(bot, update, most_expansive_card_list[0])
        telegramutils.send_message_with_card_cost(bot, update, most_expansive_card_list[0])
        if len(card_list_by_name) > 0:
            telegramutils.send_message_with_keyboard(bot, update, create_keyboard_from_card_list(card_list_by_name),
                                                     "Other cards that also contains the text you provided: ",
                                                     one_time_use=True)
            return states.PICKING
        return states.START


def get_specific_card(bot, update):
    card_name = update.message.text
    log.info('User %s is searching for the specific card %s', telegramutils.get_user_from_update(update), card_name)
    card = api.get_specific_card(card_name)
    telegramutils.send_picture(bot, update, card)
    telegramutils.send_message_with_card_cost(bot, update, card, True)
    return states.START


def abort_command(bot, update):
    log.info('User %s is aborting', telegramutils.get_user_from_update(update))
    telegramutils.send_text_message(bot, update, 'You are aborting the current search. You can start a new one')
    return states.START


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


handler_states = {
    states.START: [CommandHandler('search', search_command)],
    states.CHOOSING: [MessageHandler(Filters.text, get_named_cards), CommandHandler('abort', abort_command)],
    states.PICKING: [MessageHandler(Filters.text, get_specific_card), CommandHandler('abort', abort_command)],
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
        self.states = handler_states
        self.entry_points = [CommandHandler('search', search_command)]
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
