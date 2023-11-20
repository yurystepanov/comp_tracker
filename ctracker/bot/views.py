from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render

from product.tasks import price_change_notifications
from .tasks import send_telegram_message


# Create your views here.
@login_required
def telegram_newsletter(request):
    if request.method == "POST":
        try:
            send_telegram_message.delay(request.user.profile.telegram_user_id, 'Тестовая рассылка')
            price_change_notifications(request.user.id)
            messages.success(request, 'Рассылка отправлена')
        except Exception as e:
            messages.error(request, 'Возникла ошибка при отправке рассылки:')

    return render(request,
                  'bot/telegram.html',
                  )
