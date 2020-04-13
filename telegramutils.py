from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto


def send_message_with_keyboard(bot, update, keyboard, message, one_time_use):
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_use=one_time_use)
    bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=reply_markup)


def send_message_with_card_cost(bot, update, card, remove_keyboard=False):
    reply_markup = ReplyKeyboardRemove()
    if card['prices']['eur'] is not None:
        cost_message = "The cost of this card is: " + card['prices']['eur'] + " euro."
    else:
        cost_message = "This card has no cost"
    if remove_keyboard:
        reply_markup.remove_keyboard = True
    else:
        reply_markup.remove_keyboard = False
    bot.send_message(chat_id=update.message.chat_id, text=cost_message, reply_markup=reply_markup)


def send_text_message(bot, update, message):
    bot.send_message(chat_id=update.message.chat_id, text=message)


def send_picture(bot, update, card):
    if 'card_faces' in card.keys() and 'image_uris' not in card.keys():
        mediagroup = create_media_group_for_double_faced_cards(card['card_faces'])
        send_message_with_media_group(bot, update, mediagroup)
    else:
        bot.send_photo(chat_id=update.message.chat_id, photo=card['image_uris']['normal'])


def send_message_with_media_group(bot, update, media):
    bot.send_media_group(chat_id=update.message.chat_id, media=media)


def get_user_from_update(update):
    return update.message.from_user.username


# Method to create a media group to display more images if the card is composed by more
def create_media_group_for_double_faced_cards(card_list):
    media = []
    for card in card_list:
        media.append(InputMediaPhoto(media=card['image_uris']['normal']))
    return media
