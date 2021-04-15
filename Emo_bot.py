import time
import logging
import os
import dotenv
import psycopg2

from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, TypeHandler, Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from threading import Thread

dotenv.load_dotenv()

TELEGRAM_TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
START_MESSAGE = 'Ну привет. Я, если что, занята, отвечать не буду.'
USER_DB = os.getenv('USER_DB')
PASSWORD_DB = os.getenv('PASSWORD_DB')
HOST_DB = os.getenv('HOST')
DATABASE = os.getenv('DB')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename='main.log',
    filemode='w'
)
logger = logging.getLogger(__name__)


COUNTER = {
    'counter1': 0,
    'counter2': 0,
    'counter3': 0,
    'counter4': 0,
    'counter5': 0,
    'counter6': 0,
    }


def start(update, context):
    logging.info('сообщение отправлено в чат')
    update.message.reply_text(START_MESSAGE)


def add_reaction_bd(chat_id, user_id, message_id, callback_data):
    connection = psycopg2.connect(
        user=USER_DB,
        password=PASSWORD_DB,
        host=HOST_DB,
        database=DATABASE)
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute('INSERT INTO botemo.db_emidji VALUES (%s,%s,%s,%s) '
                       , (chat_id, message_id, user_id, callback_data))
    except:
        cursor.execute('DELETE FROM botemo.db_emidji '
                      'WHERE user_id=%s AND message_id=%s AND chat_id=%s '
                      'AND callback_data=%s',
                      (user_id, message_id, chat_id, callback_data))
    list_emodji = []
    for k in COUNTER.keys():
        cursor.execute('SELECT COUNT(*) '
                       'FROM botemo.db_emidji '
                       'WHERE message_id=%s AND chat_id=%s '
                       'AND callback_data=%s',
                       (message_id, chat_id, k))
        list_emodji.append(cursor.fetchone())
    return list_emodji


def echo(update, context):
    count = COUNTER
    buttons = [
        [
            InlineKeyboardButton(text=f'👍{count["counter1"]}', callback_data="counter1"),
            InlineKeyboardButton(text=f'👎{count["counter2"]}', callback_data="counter2"),
            InlineKeyboardButton(text=f'🤦🏻‍♂{count["counter3"]}', callback_data="counter3"),
            InlineKeyboardButton(text=f'❤️{count["counter4"]}', callback_data="counter4"),
            InlineKeyboardButton(text=f'😳{count["counter5"]}', callback_data="counter5"),
            InlineKeyboardButton(text=f'🔥{count["counter6"]}', callback_data="counter6")
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons, resize_keyboard=True)
    bot = context.bot
    text = update.message.text
    if ' /r' in text:
        bot.send_message(
            chat_id=update.message.chat.id,
            text='maybe reactions? :)',
            reply_markup=keyboard,
            api_kwargs=count
        )
    else:
        pass


def edit_button(update, context):
    data_mes = update.callback_query
    message_id = data_mes.message.message_id
    user_id = data_mes.from_user.id
    chat_id = data_mes.chat_instance
    callback_data = data_mes.data
    list_emodji = add_reaction_bd(chat_id, user_id, message_id, callback_data)
    print(list_emodji)
    query = update.callback_query.message
    buttons = [
        [
            InlineKeyboardButton(text=f'👍{list_emodji[0][0]}', callback_data="counter1"),
            InlineKeyboardButton(text=f'👎{list_emodji[1][0]}', callback_data="counter2"),
            InlineKeyboardButton(text=f'🤦🏻‍♂{list_emodji[2][0]}', callback_data="counter3"),
            InlineKeyboardButton(text=f'❤️{list_emodji[3][0]}', callback_data="counter4"),
            InlineKeyboardButton(text=f'😳{list_emodji[4][0]}', callback_data="counter5"),
            InlineKeyboardButton(text=f'🔥{list_emodji[5][0]}', callback_data="counter6")
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons, resize_keyboard=True)
    query.edit_reply_markup(
        reply_markup=keyboard
    )


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    logging.info('бот запущен')
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))
    dispatcher.add_handler(CallbackQueryHandler(edit_button, pass_chat_data=True))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
