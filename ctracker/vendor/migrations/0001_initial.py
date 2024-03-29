# Generated by Django 4.1.5 on 2023-03-29 10:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('website', models.URLField(blank=True)),
                ('image', models.ImageField(blank=True, upload_to='')),
            ],
            options={
                'verbose_name': 'vendor',
                'verbose_name_plural': 'vendors',
                'db_table': 'vendor',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='VendorLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(max_length=100)),
                ('url', models.URLField(blank=True)),
                ('target_id', models.PositiveIntegerField()),
                ('target_ct', models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'product'), ('model', 'product')), models.Q(('app_label', 'product'), ('model', 'productgroup')), _connector='OR'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vendor.vendor')),
            ],
            options={
                'verbose_name': 'vendor link',
                'verbose_name_plural': 'vendor links',
                'db_table': 'vendor_link',
            },
        ),
        migrations.CreateModel(
            name='VendorPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField()),
                ('is_current', models.BooleanField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='product.product')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vendor.vendor')),
            ],
            options={
                'verbose_name': 'price',
                'verbose_name_plural': 'prices',
                'db_table': 'vendor_price',
                'unique_together': {('vendor', 'product', 'date')},
            },
        ),
        migrations.AddIndex(
            model_name='vendorlink',
            index=models.Index(fields=['vendor', 'target_ct', 'target_id'], name='vendor_link_vendor__8b7242_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='vendorlink',
            unique_together={('vendor', 'target_ct', 'target_id', 'external_id')},
        ),
    ]
