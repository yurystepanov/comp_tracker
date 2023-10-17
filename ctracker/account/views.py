from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render

from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm


# from .models import Profile


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create a new user object but avoid saving it yet
                new_user = form.save(commit=False)
                # Set the chosen password
                new_user.set_password(form.cleaned_data['password1'])
                # Save the User object
                new_user.save()
                # Save the User Profile
                # Removed as we have signal to create profile
                # Profile.objects.create(user=new_user)
                return render(request,
                              'account/register_done.html',
                              {'new_user': new_user})
    else:
        form = UserRegistrationForm()

    return render(request,
                  'account/register.html',
                  {'form': form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.info(request, 'Изменения сохранены')
        else:
            messages.error(request, 'Ошибка сохранения профиля')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(
            instance=request.user.profile)

    return render(request,
                  'account/profile.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})
