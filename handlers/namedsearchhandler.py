from telegram import InputMediaPhoto
from telegram.ext import ConversationHandler, MessageHandler, Filters, CommandHandler

import logger
from scryfallapi import api

START, CHOOSING, TYPING_CHOICE = range(3)
log = logger.get_logger()
fallbacks=[]


def search(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Type the name of the card you want to search. It doesn't need to be the exact name")
    return CHOOSING


# Method to create a media group to display more images if the card is composed by more
def create_media_group(card_list):
    media = []
    media_one = InputMediaPhoto(media=card_list[0]['image_uris']['normal'])
    media_two = InputMediaPhoto(media=card_list[1]['image_uris']['normal'])
    media.append(media_one)
    media.append(media_two)
    return media


def get_named_cards(bot, update):
    card_name = update.message.text
    log.info('User is searching for the card %s', card_name)
    card_list, double_faced = api.get_most_expansive_card(card_name)
    if len(card_list) == 0:
        bot.send_message(chat_id=update.message.chat_id, text="No cards found with the text that you typed, type a new "
                                                              "name")
        return CHOOSING
    else:
        if not double_faced:
            card_image = card_list[0]['image_uris']['normal']
            bot.send_photo(chat_id=update.message.chat_id, photo=card_image)
        else:
            media = create_media_group(card_list)
            bot.send_media_group(chat_id=update.message.chat_id, media=media)
        cost_message = 'The cost of this card is: ' + card_list[0]['eur'] + ' euro'
        bot.send_message(chat_id=update.message.chat_id, text=cost_message)
        return START


def search_interrupted(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Search interrupted.")


states = {
    START: [CommandHandler('search', search)],
    CHOOSING: [MessageHandler(Filters.text, get_named_cards)],
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
        self.fallbacks = fallbacks
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






