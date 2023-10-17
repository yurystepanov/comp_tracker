from celery import shared_task
from bot.tasks import send_telegram_message

from django.conf import settings
from datetime import date

from account.models import Profile
from product.models import Product


@shared_task(name="price_change_notifications")
def price_change_notifications(user_id=''):
    profiles = Profile.objects.filter(telegram_verified=True).exclude(
        telegram_user_id__exact='').select_related('user')

    if user_id:
        profiles.filter(user__id=user_id)
    else:
        profiles.filter(allow_notifications=True)

    subject = f'Цены комплектующих на {date.today()}\n.........................\n\n'

    for profile in profiles:
        products = Product.objects.filter(subscriptions=profile.user).order_by('group__order')
        message = '\n...\n'.join([f'{product.name}: {product.price()}' for product in products])

        send_telegram_message.delay(profile.telegram_user_id, subject + message)
