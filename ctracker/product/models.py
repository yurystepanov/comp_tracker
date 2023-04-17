from itertools import groupby

from django.core.cache import cache
from django.db import models
from django.db.models import Exists, OuterRef, Min, Max, Q
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytils.translit import slugify


class Brand(models.Model):
    """
    Model, representing brand of a product; e.g. "Intel", "AMD", "NVIDIA"
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100)
    image = models.ImageField(blank=True, upload_to='images/brands/')

    class Meta:
        ordering = ['name']
        verbose_name = 'brand'
        verbose_name_plural = 'brands'
        db_table = "product_brand"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductGroup(models.Model):
    """
    Model, representing product group; e.g. "Processors", "Motherboards"
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100)
    order = models.IntegerField(default=0, blank=True)
    image = models.ImageField(blank=True, upload_to='images/groups/')
    imageURL = models.URLField(blank=True)
    root = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
        verbose_name = 'product group'
        verbose_name_plural = 'product groups'
        db_table = 'product_group'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if not self.root:
            return reverse('product:product_list',
                           args=[self.id, self.slug])
        return reverse('product:products')

    @property
    def updated_at(self):
        return self.contains.aggregate(Max('updated_at')).get('updated_at__max')


class Product(models.Model):
    """
    Model, representing product; e.g. "Processor AMD Ryzen 5 2600, SocketAM4, OEM"
    """
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)
    brand = models.ForeignKey(Brand, on_delete=models.RESTRICT, related_name='produces')
    group = models.ForeignKey(ProductGroup, on_delete=models.RESTRICT, related_name='contains')
    description_short = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(blank=True, upload_to='images/products/')
    imageURL = models.URLField(blank=True)

    favourites = models.ManyToManyField(get_user_model(),
                                        related_name='favourite_products',
                                        blank=True,
                                        db_table='product_favourites'
                                        )

    subscriptions = models.ManyToManyField(get_user_model(),
                                           related_name='subscribed_products',
                                           blank=True,
                                           db_table='product_subscriptions'
                                           )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'product'
        verbose_name_plural = 'products'
        db_table = 'product'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product:product_detail',
                       args=[self.id, self.slug])

    def __str__(self):
        return self.name

    def get_prices(self, is_current=True):
        """
        Returns QuerySet with current prices for Product
        """
        return self.prices.filter(is_current=is_current, price__gt=0)

    def current_price_object(self) -> 'vendor.VendorPrice':
        """
        Returns current VendorPrice for Product. If no price exists - returns None
        """
        price_object = self.get_prices().order_by('price')[:1]
        return price_object[0] if price_object else None

    # @property
    def price(self):
        """
        Returns current minimum price for Product. If no price exists - returns None
        """
        key = (self.id, 'curr_price')
        price = cache.get(key)

        if not price:
            price_object = self.current_price_object()
            price = price_object.price if price_object else None
            cache.set(key, price)

        return price

    def prev_price(self):
        """
        Returns closest vendors price that differs from the current price
        """
        key = (self.id, 'prev_price')
        prev_price = cache.get(key)

        if not prev_price:
            price_object = self.current_price_object()
            if price_object:
                current_price_date = price_object.date

                qs = self.prices.filter(~Q(price=price_object.price), date__lt=current_price_date).annotate(
                    last_price=Exists(
                        self.prices.filter(product=OuterRef('product'),
                                           vendor=OuterRef('vendor'),
                                           date__gt=OuterRef('date'),
                                           date__lt=current_price_date),
                        ~Q(price=price_object.price)
                    ))

                last_prices = qs.filter(last_price=False, price__gt=0).aggregate(Min('price'))

                prev_price = last_prices.get('price__min')
                cache.set(key, prev_price)
        return prev_price


class SpecificationGroup(models.Model):
    """
    Model, representing group of product specifications; e.g. "Common parameters", "Manufacturing data" to keep product
    specifications in order
    """
    name = models.CharField(max_length=100, unique=True)
    order = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'specification group'
        verbose_name_plural = 'specification groups'
        db_table = 'specification_group'


class Specification(models.Model):
    """
    Model, representing specifications; e.g. "Voltage", "Cores", "Socket" etc.
    """
    name = models.CharField(max_length=100)
    group = models.ForeignKey(SpecificationGroup, on_delete=models.CASCADE)
    order = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'specification'
        verbose_name_plural = 'specifications'
        unique_together = ['group', 'name']
        db_table = 'specification'


class SpecificationValue(models.Model):
    """
    Model, representing specifications of concrete product; e.g. product: Core i3-12100F OEM has 12 month of warranty,
    6 cores, socket LGA 1700.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    specification = models.ForeignKey(Specification, on_delete=models.CASCADE)
    value = models.CharField(max_length=400)

    class Meta:
        verbose_name = 'specification value'
        verbose_name_plural = 'specification values'
        unique_together = ['product', 'specification']
        db_table = 'specification_value'

    def __str__(self):
        return f'{self.product}: [{self.specification}] -> {self.value}'


class ProductFilter(models.Model):
    """
    Model, representing specifications selected for filtering of products in a product group
    Available filters on product_list page
    """
    group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE)
    specification = models.ForeignKey(Specification, on_delete=models.CASCADE, related_name='filtering')
    order = models.IntegerField(default=0, blank=True)
    filter_name = models.CharField(max_length=20)

    class Meta:
        unique_together = ['group', 'specification']
        verbose_name = 'filter'
        verbose_name_plural = 'filters'
        ordering = ['group', 'order']
        db_table = 'product_filter'

    def __str__(self):
        return f'{self.group}: {self.specification}'


def annotate_queryset_with_price(product_queryset, product_path=''):
    """
    Adds minimum price annotation as price to QuerySet containing Product

    product_path - str, path to product in queryset. if QuerySet.Model != Product
    parameter is mandatory
    """
    if product_queryset.model != Product and not product_path:
        raise Exception('product_name should be specified')

    if product_path:
        product_path += '__'

    product_queryset = product_queryset.filter(**{f'{product_path}prices__is_current': True,
                                                  f'{product_path}prices__price__gt': 0
                                                  }). \
        annotate(price=models.Min(f'{product_path}prices__price'))

    return product_queryset


def make_product_group_spec_queryset(product_group):
    """
    Returns QuerySet with all ProductGroup filters and it's values in one query. Ordered in filter + filter values order
    """

    filter_values = SpecificationValue.objects.filter(product__group=product_group,
                                                      specification__filtering__group=product_group) \
        .values('value', 'specification', 'specification__filtering__filter_name', 'specification__name') \
        .order_by('specification__filtering__order', 'specification__filtering__filter_name',
                  'value').distinct()

    return groupby(filter_values,
                   key=lambda item: [item['specification__filtering__filter_name'], item['specification__name']])


def get_favourites_list(user):
    """
    Return a list of Product objects id's favourite to user
    parameter: User
    """
    return Product.objects.values_list('id', flat=True).filter(favourites=user)


def get_subscriptions_list(user):
    """
    Return a list of Product objects id's user is subscribed to
    parameter: User
    """
    return Product.objects.values_list('id', flat=True).filter(subscriptions=user)
