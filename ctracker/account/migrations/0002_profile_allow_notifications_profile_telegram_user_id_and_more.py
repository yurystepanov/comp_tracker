# Generated by Django 4.1.5 on 2023-04-19 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='allow_notifications',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='telegram_user_id',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='profile',
            name='telegram_verification_code',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='telegram_verified',
            field=models.BooleanField(default=False),
        ),
    ]
