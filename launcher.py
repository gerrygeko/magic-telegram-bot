import logger
import telegramutils

from telegram.ext import Updater, CommandHandler

from handlers.namedsearchhandler import NamedSearchHandler
from scryfallapi import api

log = logger.get_logger()
TOKEN = '748543401:AAG75JbeJwztGeenL-LUw-dev6CWkHQF-Wk'


def start(bot, update):
    log.info('Start command called')
    telegramutils.send_text_message(bot, update, "Welcome to Magic Search Bot. To start searching for a card type "
                                                 "/search.")


def random(bot, update):
    log.info('Visualize a random card')
    card = api.get_random_card()
    log.info(card['image_uris']['normal'])
    telegramutils.send_picture(bot, update, card)


def help(bot, update):
    log.info('Help command called')
    telegramutils.send_text_message(bot, update, 'Click the "/" to list all commands or type /start to start searching')


def error(update, context):
    """Log Errors caused by Updates."""
    log.warning('Update "%s" caused error "%s"', update, error)


def create_dispatcher(updater):
    dp = updater.dispatcher
    start_handler = CommandHandler(command='start', callback=start)
    named_handler = NamedSearchHandler()
    random_handler = CommandHandler(command='random', callback=random)
    help_handler = CommandHandler(command='help', callback=help)
    dp.add_handler(start_handler)
    dp.add_handler(named_handler)
    dp.add_handler(random_handler)
    dp.add_handler(help_handler)
    log.info('Handler registered')
    dp.add_error_handler(error)
    return dp


if __name__ == '__main__':
    log.info('Booting the bot')
    updater = Updater(token=TOKEN)
    dispatcher = create_dispatcher(updater=updater)
    updater.start_polling()