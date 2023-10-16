import random

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings

from assembly.models import Assembly


class Profile(models.Model):
    """
    Model representing Assembly contents, linking Assembly and Products with extra data - quantity
    Part of a concrete computer is AssemblyComponent while computer is an Assembly
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/',
                              blank=True)

    default_assembly = models.OneToOneField(Assembly,
                                            null=True,
                                            on_delete=models.DO_NOTHING,
                                            related_name='default_for')

    allow_notifications = models.BooleanField(default=False)
    telegram_user_id = models.CharField(max_length=100, blank=True)
    telegram_verified = models.BooleanField(default=False)
    telegram_verification_code = models.IntegerField(default=0)

    def __str__(self):
        return f'Profile of {self.user.username}'


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, telegram_verification_code=random.randrange(1000, 10000))


post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)
