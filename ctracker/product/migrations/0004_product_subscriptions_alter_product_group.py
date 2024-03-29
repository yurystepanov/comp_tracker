# Generated by Django 4.1.5 on 2023-04-07 13:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('product', '0003_alter_specificationvalue_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='subscriptions',
            field=models.ManyToManyField(blank=True, db_table='product_subscriptions', related_name='subscribed_products', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='product',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='contains', to='product.productgroup'),
        ),
    ]
