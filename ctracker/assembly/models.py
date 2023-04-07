from django.contrib.auth import get_user_model
from django.db import models
from pytils.translit import slugify

from product.models import Product, annotate_queryset_with_price


class Assembly(models.Model):
    """
    Model, combining a set of products to a named object - Assembly.
    e.g. Computer is an assembly
    """
    name = models.CharField(max_length=100, verbose_name='Имя сборки')
    slug = models.SlugField(max_length=100)
    description_short = models.CharField(max_length=200, blank=True, verbose_name='Описание')
    # Common assemblies has no owner
    owner = models.ForeignKey(get_user_model(),
                              on_delete=models.CASCADE,
                              null=True,
                              blank=True,
                              related_name='owns_assemblies'
                              )
    component = models.ManyToManyField(Product,
                                       through='AssemblyComponent',
                                       related_name='contains',
                                       blank=True
                                       )

    class Meta:
        verbose_name = 'assembly'
        verbose_name_plural = 'assemblies'
        db_table = 'assembly'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def total_value(self):
        return sum(product.price for product in annotate_queryset_with_price(self.component.all()))

    def image(self):
        pass

    def imageURL(self):
        case = self.component.filter(group__name='Корпуса').first()
        return case.imageURL if case else ''


class AssemblyComponent(models.Model):
    """
    Model representing Assembly contents, linking Assembly and Products with extra data - quantity
    Part of a concrete computer is AssemblyComponent while computer is an Assembly
    """
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='in_components')
    quantity = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'assembly component'
        verbose_name_plural = 'assembly components'
        db_table = 'assembly_component'

    def value(self):
        return self.quantity * self.product.price()
