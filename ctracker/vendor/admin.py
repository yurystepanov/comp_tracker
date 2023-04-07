from django.contrib import admin

from .models import Vendor, VendorPrice, VendorLink


# Register your models here.
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'website']
    search_fields = ['name']
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(VendorPrice)
class VendorPriceAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'product', 'price', 'is_current', 'date']
    list_filter = ['vendor__name', 'date', 'is_current']
    search_fields = ['product__name']
    autocomplete_fields = ['product']


@admin.register(VendorLink)
class VendorLinkAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'target_ct', 'target', 'external_id', 'url']
    list_filter = ['vendor', 'target_ct']
    search_fields = ['external_id']
