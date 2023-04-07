from django.contrib import admin
from django.contrib.admin import TabularInline

from .models import Assembly, AssemblyComponent


# Register your models here.
class AssemblyComponentInLine(TabularInline):
    model = AssemblyComponent
    extra = 1
    autocomplete_fields = ['product']
    fields = ['product', 'quantity']


@admin.register(Assembly)
class AssemblyAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'slug']
    list_filter = ['owner']
    search_fields = ['name']
    ordering = ['owner', 'name']
    list_per_page = 20

    inlines = [AssemblyComponentInLine]
