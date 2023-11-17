from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.forms.fields import EmailField

from .models import Profile


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email')

        field_classes = {'username': UsernameField,
                         'email': EmailField,
                         }


class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']


class ProfileEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        self.fields['telegram_verification_code'].disabled = True

    class Meta:
        model = Profile
        fields = ['date_of_birth',
                  'photo',
                  'telegram_verification_code',
                  ]
