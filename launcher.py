import os

from telegram import Update

import logger
import telegramutils

from telegram.ext import Updater, CommandHandler, CallbackContext
from handlers.namedsearchhandler import conversation_handler
from scryfallapi import api

log = logger.get_logger()


def start_function(update: Update, context: CallbackContext):
    log.info('Start command called')
    telegramutils.send_text_message(context.bot, update, 'Welcome to Magic Search Bot. To start searching '
                                                         'for a card type /search.')


def random_function(update: Update, context: CallbackContext):
    log.info('Visualize a random card')
    card = api.get_random_card()
    log.info(card['image_uris']['normal'])
    telegramutils.send_picture(context.bot, update, card)


def help_function(update: Update, context: CallbackContext):
    log.info('Help command called')
    telegramutils.send_text_message(context.bot, update, 'Click the "/" to list all commands or '
                                                         'type /start to start searching')


def exit_function(update: Update, context: CallbackContext):
    log.info('User is aborting')
    telegramutils.send_text_message(context.bot, update, 'You are exiting the current operation. Type /search '
                                                         'for a new search or /help to get the list of the commands')


def error(update, context):
    """Log Errors caused by Updates."""
    log.warning('Update "%s" caused error "%s"', update, context.error)


def create_dispatcher(updater):
    dp = updater.dispatcher
    exit_handler = CommandHandler(command='exit', callback=exit_function)
    start_handler = CommandHandler(command='start', callback=start_function)
    named_handler = conversation_handler
    random_handler = CommandHandler(command='random', callback=random_function)
    help_handler = CommandHandler(command='help', callback=help_function)
    dp.add_handler(exit_handler)
    dp.add_handler(start_handler)
    dp.add_handler(named_handler)
    dp.add_handler(random_handler)
    dp.add_handler(help_handler)
    dp.add_error_handler(error)
    log.info('Handlers registered')
    return dp


def load_token_from_file():
    with open(os.path.dirname(os.path.realpath(__file__)) + '\\token') as file:
        token = file.readline().strip()
    return token


if __name__ == '__main__':
    log.info('Booting the bot')
    token = load_token_from_file()
    updater = Updater(token=token, use_context=True)
    dispatcher = create_dispatcher(updater=updater)
    updater.start_polling()
