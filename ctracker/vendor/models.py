from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction

from product.models import Product


# Create your models here.
class Vendor(models.Model):
    """
    Model, representing vendor; e.g. "DNS", "CITILINK"
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    image = models.ImageField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'vendor'
        verbose_name_plural = 'vendors'
        db_table = 'vendor'

    def __str__(self):
        return self.name


class CurrentManager(models.Manager):
    """
    ContentManager to return current prices
    """

    def get_queryset(self):
        return super().get_queryset().filter(isCurrent=True)


def get_current_price(product, vendor):
    """
    Returns VendorProductPrice object with current price for product and vendor

    Parameters
    product: Product, vendor: Vendor

    Returns
    VendorProductPrice
    """
    current_price = VendorPrice.objects.filter(product=product, vendor=vendor, is_current=True).first()

    return current_price


class VendorPrice(models.Model):
    """
    Model, representing vendor's product price by date; Current price is marked is_current = True
    """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    is_current = models.BooleanField()

    objects = models.Manager()  # The default manager.
    current = CurrentManager()  # Current price manager.

    class Meta:
        unique_together = ['vendor', 'product', 'date']
        verbose_name = 'price'
        verbose_name_plural = 'prices'
        db_table = 'vendor_price'

    def __str__(self):
        return (f'Product: {self.product} Vendor: {self.vendor} Price '
                f'{self.price} Date: {self.date} Current: {self.is_current}')

    def save(self, force_is_current=False, *args, **kwargs):
        with transaction.atomic():

            if not force_is_current:
                current_price = get_current_price(product=self.product, vendor=self.vendor)
                if current_price and current_price.date < self.date:
                    current_price.is_current = False
                    current_price.save(force_is_current=True)

                if not current_price:
                    self.is_current = True
                elif current_price.date < self.date:
                    self.is_current = True
                else:
                    self.is_current = self.date == current_price.date

            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)

            if self.is_current:
                last_price = VendorPrice.objects.filter(product=self.product,
                                                        vendor=self.vendor).order_by('-date').first()

                if last_price:
                    last_price.is_current = True
                    last_price.save()

    def external(self):
        return VendorLink.objects.filter(vendor=self.vendor,
                                         target_id=self.product.id,
                                         target_ct=ContentType.objects.get_for_model(Product)).first()


class VendorLink(models.Model):
    """
    Model, representing links between vendor's data and product catalog objects
    external_id - vendor's id of object in product catalog
    url - link to vendor's web-site, representing product catalog object
    """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    external_id = models.CharField(max_length=100)
    url = models.URLField(max_length=200, blank=True)

    limit = models.Q(app_label='product', model='product') | models.Q(app_label='product', model='productgroup')

    target_ct = models.ForeignKey(ContentType,
                                  limit_choices_to=limit,
                                  on_delete=models.CASCADE,
                                  )
    target_id = models.PositiveIntegerField()
    target = GenericForeignKey('target_ct', 'target_id')

    class Meta:
        indexes = [
            models.Index(fields=['vendor', 'target_ct', 'target_id']),
        ]
        unique_together = ['vendor', 'target_ct', 'target_id', 'external_id']
        db_table = 'vendor_link'
        verbose_name = 'vendor link'
        verbose_name_plural = 'vendor links'

    def __str__(self):
        return f'{self.vendor} {self.target} {self.external_id}'
