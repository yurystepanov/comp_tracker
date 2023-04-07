from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    # post views
    path('register/', views.register, name='register'),
    path('profile/', views.edit, name='profile'),
]
