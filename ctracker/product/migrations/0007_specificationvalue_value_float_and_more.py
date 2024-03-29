# Generated by Django 4.1.5 on 2023-11-30 06:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_productfilter_display_widget'),
    ]

    operations = [
        migrations.AddField(
            model_name='specificationvalue',
            name='value_float',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='specificationvalue',
            name='specification',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specvalues', to='product.specification'),
        ),
    ]
