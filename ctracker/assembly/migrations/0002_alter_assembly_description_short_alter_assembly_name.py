# Generated by Django 4.1.5 on 2023-04-07 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assembly', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assembly',
            name='description_short',
            field=models.CharField(blank=True, max_length=200, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='assembly',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Имя сборки'),
        ),
    ]
