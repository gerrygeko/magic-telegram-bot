import logger

from telegram.ext import Updater, CommandHandler
from scryfallapi import apirandom

log = logger.get_logger()
TOKEN = '748543401:AAG75JbeJwztGeenL-LUw-dev6CWkHQF-Wk'


def start(bot, update):
    log.info('Start command called')
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def random(bot, update):
    log.info('Visualize a random card')
    card = apirandom.get_random_card()
    print(card['image_uris']['normal'])
    bot.send_photo(chat_id=update.message.chat_id, photo=card['image_uris']['normal'])


def create_dispatcher(updater):
    dp = updater.dispatcher
    start_handler = CommandHandler(command='start', callback=start)
    random_handler =CommandHandler(command='random', callback=random)
    dp.add_handler(start_handler)
    dp.add_handler(random_handler)
    log.info('Handler registered')
    return dp


if __name__ == '__main__':
    log.info('Booting the bot')
    updater = Updater(token=TOKEN)
    dispatcher = create_dispatcher(updater=updater)
    updater.start_polling()