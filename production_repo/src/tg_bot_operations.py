import telebot

from config import Config
from logger import logger

config_ = Config()

bot = telebot.TeleBot(config_.telegram_api_key)


def send_message(message):
    try:
        bot.send_message(chat_id=config_.group_id, text=message)
    except Exception as e:
        logger.error(f"Error sending message: {e}")


def send_message_to_xtayl_events(message):
    try:
        bot.send_message(chat_id=config_.xtayl_events, text=message)
    except Exception as e:
        logger.error(f"Error sending message to xtayl events: {e}")


def send_plot(buf, caption):
    try:
        bot.send_photo(chat_id=config_.group_id, photo=buf, caption=caption)
    except Exception as e:
        logger.error(f"Error sending image: {e}")
    finally:
        buf.close()
