import logging
from telegram.ext import Updater, CommandHandler

log = None
TOKEN = '748543401:AAG75JbeJwztGeenL-LUw-dev6CWkHQF-Wk'


def set_logger():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


def start(bot, update):
    log.info('Start command called')
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def create_dispatcher(updater):
    dp = updater.dispatcher
    start_handler = CommandHandler(command='start', callback=start)
    dp.add_handler(start_handler)
    log.info('Handler registered')
    return dp


if __name__ == '__main__':
    log = set_logger()
    log.info('Booting the bot')
    updater = Updater(token=TOKEN)
    dispatcher = create_dispatcher(updater=updater)
    updater.start_polling()