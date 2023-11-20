from django.urls import path

from . import views

app_name = 'telegram'

urlpatterns = [
    path('newsletter', views.telegram_newsletter, name='telegram_newsletter'),
]
