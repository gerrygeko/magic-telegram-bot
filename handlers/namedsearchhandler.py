from telegram import InputMediaPhoto, KeyboardButton, Update
from telegram.ext import ConversationHandler, MessageHandler, Filters, CommandHandler, CallbackContext
from emoji import emojize

import logger
import telegramutils
from scryfallapi import api, bot_state

states = bot_state.NamedSearchStates
log = logger.get_logger()
abort_emoji = emojize(":x:", use_aliases=True)


def search_command(update: Update, context: CallbackContext):
    log.info('User %s is in the suggestion phase', telegramutils.get_user_from_update(update))
    telegramutils.send_text_message(context.bot, update,
                                    "Type the name of the card you want to search. It doesn't need to be the exact "
                                    "name. The most expansive one will be showed. "
                                    "You can abort at any moment the search by executing the /abort command")
    return states.CHOOSING


def get_named_cards(update: Update, context: CallbackContext):
    card_name = update.message.text
    log.info('User %s is searching for cards that contain in the text name the word: %s',
             telegramutils.get_user_from_update(update), card_name)
    expensive_card = api.get_most_expansive_card(card_name)
    if expensive_card is None:
        telegramutils.send_text_message(context.bot, update, "No cards found with the text that you typed, "
                                                             "type a new name")
        return states.CHOOSING
    else:
        telegramutils.send_picture(context.bot, update, expensive_card)
        telegramutils.send_message_with_card_cost(context.bot, update, expensive_card)
        card_list_by_name = api.get_list_card_by_name(card_name)
        if len(card_list_by_name) > 1:
            telegramutils.send_message_with_keyboard(context.bot, update, create_keyboard_from_card_list(card_list_by_name),
                                                     "Other cards that also contains the text you provided: ",
                                                     one_time_use=True)
            return states.PICKING
        return states.START


def get_specific_card(update: Update, context: CallbackContext):
    card_name = update.message.text
    user_name = telegramutils.get_user_from_update(update)
    log.info('User %s is searching for the specific card %s', user_name, card_name)
    card = api.get_specific_card(card_name)
    context.user_data['card_name'] = card['name']
    card_reprints = api.get_list_card_for_reprints(card['prints_search_uri'])
    context.user_data['card_reprints'] = card_reprints
    telegramutils.send_picture(context.bot, update, card)
    telegramutils.send_message_with_card_cost(context.bot, update, card, True)
    telegramutils.send_message_with_keyboard(context.bot, update, create_keyboard_for_card_reprint(card_reprints),
                                             "Other prints for the specific card: ",
                                             one_time_use=True)
    return states.PRINTING


def get_specific_printing(update: Update, context: CallbackContext):
    set_name = update.message.text
    if set_name == '{} Abort'.format(abort_emoji):
        telegramutils.send_text_message(context.bot, update, 'You can search for a new card')
        return states.CHOOSING
    card_name = context.user_data['card_name']
    card_reprints = context.user_data['card_reprints']
    user_name = telegramutils.get_user_from_update(update)
    card = get_specific_reprint_from_list_by_set(card_reprints, set_name)
    log.info('User %s is searching for the printing of card %s contained in the set %s', user_name, card_name, set_name)
    text = "Set: {}".format(set_name)
    telegramutils.send_picture(context.bot, update, card)
    telegramutils.send_text_message(context.bot, update, text)
    telegramutils.send_message_with_card_cost(context.bot, update, card)
    return states.PRINTING


def abort_command(update: Update, context: CallbackContext):
    log.info('User %s is aborting', telegramutils.get_user_from_update(update))
    telegramutils.send_text_message(context.bot, update, 'You are aborting the current /search. You can start a new one')
    return states.START


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


def create_keyboard_for_card_reprint(card_list):
    keyboard = []
    row = None
    first_element = True
    for i in range(0, len(card_list)):
        if first_element:
            row = [KeyboardButton(text=card_list[i]['set_name'])]
            first_element = False
        else:
            row.append(KeyboardButton(text=card_list[i]['set_name']))
            keyboard.append(row)
            first_element = True
    row = [KeyboardButton(text=abort_emoji + " Abort")]
    keyboard.append(row)
    return keyboard


def get_specific_reprint_from_list_by_set(card_reprints, set_name):
    for card in card_reprints:
        if card['set_name'] == set_name:
            return card
    return None


handler_states = {
    states.START: [CommandHandler('search', search_command)],
    states.CHOOSING: [MessageHandler(Filters.text, get_named_cards), CommandHandler('abort', abort_command)],
    states.PICKING: [MessageHandler(Filters.text, get_specific_card), CommandHandler('abort', abort_command)],
    states.PRINTING: [MessageHandler(Filters.text, get_specific_printing), CommandHandler('abort', abort_command)]
}

conversation_handler = ConversationHandler(states=handler_states,
                                           entry_points=[CommandHandler('search', search_command)],
                                           fallbacks=[])

