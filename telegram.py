import logging
import flask
import telebot
import config
import api

API_TOKEN = config.API_TOKEN

WEBHOOK_HOST = config.WEBHOOK_HOST
WEBHOOK_PORT = config.WEBHOOK_PORT
WEBHOOK_LISTEN = config.WEBHOOK_LISTEN

WEBHOOK_SSL_CERT = config.WEBHOOK_SSL_CERT
WEBHOOK_SSL_PRIV = config.WEBHOOK_SSL_PRIV

WEBHOOK_URL_BASE = config.WEBHOOK_URL_BASE
WEBHOOK_URL_PATH = config.WEBHOOK_URL_PATH

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)

app = flask.Flask(__name__)

def generate_keyboard(keys, message, telegram_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    for key, value in keys.items():
        keyboard.add(telebot.types.InlineKeyboardButton(text=value, callback_data=key))
    bot.send_message(chat_id=telegram_id, text=message, reply_markup=keyboard)

@bot.message_handler(commands=['start', 'help', 'test'])
def send_welcome(message):
    if api.check_access(telegram_id=message.from_user.id):
        keys = api.user_message_processing(telegram_id=message.from_user.id, message=message.text)
        generate_keyboard(keys=keys[0], message=keys[1], telegram_id=message.from_user.id)
    else:
        bot.send_message(message.chat.id, 'Access denied')

# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'ggwphf'

# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)

# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    if api.check_access(telegram_id=message.from_user.id):
        text_responce = api.user_message_processing(telegram_id=message.chat.id, message=message.text)
        if isinstance(text_responce, tuple):
            generate_keyboard(keys=text_responce[0], message=text_responce[1], telegram_id=message.from_user.id)
        else:
            bot.send_message(message.chat.id, text_responce or message.text)
    else:
        bot.send_message(message.chat.id, 'Access denied')

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message and api.check_access(telegram_id=call.message.chat.id):
        text_responce = api.user_message_processing(telegram_id=call.message.chat.id, message=call.data)
        if isinstance(text_responce, tuple):
            generate_keyboard(keys=text_responce[0], message=text_responce[1], telegram_id=call.message.chat.id)
        else:
            bot.send_message(call.message.chat.id, text_responce)
    else:
        bot.send_message(call.message.chat.id, 'Access denied')


app.run(host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV), debug=True)