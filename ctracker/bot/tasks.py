from celery import shared_task
from telebot import TeleBot

from django.conf import settings


@shared_task(name="send_telegram_message")
def send_telegram_message(chat_id, text, *args, **kwargs):
    bot = TeleBot(settings.TELEGRAM_BOT_API_KEY, threaded=False)
    bot.send_message(chat_id=chat_id, text=text, *args, **kwargs)
