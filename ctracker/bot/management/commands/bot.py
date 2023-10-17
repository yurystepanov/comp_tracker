from django.core.management.base import BaseCommand
from django.conf import settings
from telebot import TeleBot, types

from account.models import Profile
from product.tasks import price_change_notifications

# Объявление переменной бота
bot = TeleBot(settings.TELEGRAM_BOT_API_KEY, threaded=False)


# Название класса обязательно - "Command"
class Command(BaseCommand):
    # Используется как описание команды обычно
    help = 'Implemented to Django application telegram bot setup command'

    def handle(self, *args, **kwargs):
        bot.enable_save_next_step_handlers(delay=2)  # Сохранение обработчиков
        bot.load_next_step_handlers()  # Загрузка обработчиков
        bot.infinity_polling()


def telegram_to_user(telegram_user_id):
    profile = Profile.objects.filter(telegram_user_id=telegram_user_id, telegram_verified=True).first()

    return profile.user if profile else None


@bot.message_handler(commands=['start'])
def start_message(message):
    user = telegram_to_user(message.chat.id)

    if not user:
        bot.send_message(message.chat.id,
                         ('Отправьте команду /register username code, где username - пользователь ctracker, '
                          'а code - код проверки телеграм в профиле пользователя'))
    else:
        bot.send_message(message.chat.id, text=f'Привет, {user.username}')


@bot.message_handler(commands=['register'])
def register_message(message):
    parm = message.text.split()
    username = parm[1] if len(parm) > 1 else ''
    code = parm[2] if len(parm) > 2 else ''

    if not username:
        bot.send_message(message.chat.id, text='Не указан username')
    if not code:
        bot.send_message(message.chat.id, text='Не указан code')

    if not username or not code:
        return

    profile = Profile.objects.filter(user__username=username).first()

    if profile and str(profile.telegram_verification_code) == code:
        profile.telegram_user_id = message.chat.id
        profile.telegram_verified = True
        profile.save()
        bot.send_message(message.chat.id, text=f'Регистрация пройдена, {profile.user.username}')
    else:
        bot.send_message(message.chat.id,
                         text=f'Пользователь {username} не существует или код проверки неправильный')


@bot.message_handler(commands=['prices'])
def start_message(message):
    user = telegram_to_user(message.chat.id)

    if user:
        price_change_notifications.delay(user.id)
    else:
        bot.send_message(message.chat.id,
                         ('Отправьте команду /register username code, где username - пользователь ctracker, '
                          'а code - код проверки телеграм в профиле пользователя'))
