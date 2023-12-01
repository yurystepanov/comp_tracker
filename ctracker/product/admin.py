from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import (ProductGroup, Brand, Product, SpecificationGroup, Specification, SpecificationValue,
                     ProductFilter)
from vendor.models import VendorLink

# Register your models here.
admin.site.register(SpecificationGroup)


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'group']
    list_filter = ['group', 'filtering__group__name']
    search_fields = ['name']


@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'root']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    list_filter = ['produces__group']
    search_fields = ['name', 'slug']
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}

    actions = ['re_save']

    @admin.action(description='Resave selected records (re-slugify)')
    def re_save(self, request, queryset):
        for brand in queryset:
            brand.save()


@admin.register(SpecificationValue)
class SpecificationValueAdmin(admin.ModelAdmin):
    list_display = ['product', 'specification', 'value']
    list_filter = ['specification']
    search_fields = ['value']


class VendorLinkInLine(GenericTabularInline):
    model = VendorLink
    ct_field = 'target_ct'
    ct_fk_field = 'target_id'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'group', 'description_short']
    list_filter = ['group']
    search_fields = ['name', 'description_short']
    ordering = ['group', 'name']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20

    inlines = [
        VendorLinkInLine,
    ]


@admin.register(ProductFilter)
class ProductFilterAdmin(admin.ModelAdmin):
    list_display = ['group', 'specification', 'order', 'filter_name', 'display_widget']
    list_filter = ['group']
    search_fields = ['specification']
    ordering = ['group', 'order']
    autocomplete_fields = ['specification']
    search_fields = ['name', 'filter_name']
