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


def get_named_cards(bot, update, user_data):
    card_name = update.message.text
    log.info('User is searching for the card %s', card_name)
    card = api.get_named_card(card_name)
    bot.send_photo(chat_id=update.message.chat_id, photo=card['data'][0]['image_uris']['normal'])
    return START


def search_interrupted(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Search interrupted.")

states = {
    START: [CommandHandler('search', search)],
    CHOOSING: [MessageHandler(Filters.text, get_named_cards, pass_user_data=True)],
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






