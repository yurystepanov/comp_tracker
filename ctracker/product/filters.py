from dataclasses import dataclass
from typing import List

from django.db.models import Max, Min

from cache_memoize import cache_memoize

from .models import SpecificationValue, ProductFilter
from assembly.services import UserAssembly

import django_filters
from django.forms.widgets import CheckboxInput

from common.widgets import DividedRangeWidget
from common.filters import ExtraPredicateMultipleChoiceMixin, ExtraPredicateFilterMixin

CACHE_TIMEOUT = 600


@dataclass
class ProductFilterDC:
    group_id: int
    specification_id: int
    specification_name: str
    filter_name: str
    display_widget: str


def _specification_values(product_specification_id: int, product_group_id: int):
    return SpecificationValue.objects.filter(
        specification=product_specification_id, product__group=product_group_id).all()


@cache_memoize(CACHE_TIMEOUT)
def filter_by_group(product_group_id: int) -> List[ProductFilterDC]:
    product_filters = (ProductFilter.objects.filter(group=product_group_id)
                       .order_by('order', 'specification__name')
                       .select_related('specification')
                       )

    return [ProductFilterDC(group_id=product_group_id,
                            specification_id=item.specification.id,
                            specification_name=item.specification.name,
                            filter_name=item.filter_name,
                            display_widget=item.display_widget
                            ) for item in product_filters]


@cache_memoize(CACHE_TIMEOUT)
def filter_choices(product_specification_id: int, product_group_id: int):
    sv = _specification_values(product_specification_id, product_group_id).values(
        'value').order_by('value').distinct()

    return [item['value'] for item in sv]


@cache_memoize(CACHE_TIMEOUT)
def filter_max_and_min_values(product_specification_id: int, product_group_id: int):
    sv = _specification_values(product_specification_id, product_group_id).aggregate(Max('value_float'),
                                                                                     Min('value_float'))
    max_value = int(sv['value_float__max'])
    min_value = int(sv['value_float__min'])

    return min_value, max_value


class SpecMultipleChoiceFilter(ExtraPredicateMultipleChoiceMixin, django_filters.MultipleChoiceFilter):
    pass


class SpecRangeFilter(ExtraPredicateFilterMixin, django_filters.RangeFilter):
    pass


class ProductFilterSet(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name='name', label='Поиск', lookup_expr='icontains')
    brand = django_filters.CharFilter(field_name='brand__name', label='Бренд', lookup_expr='icontains')

    price = django_filters.RangeFilter(field_name='price', label='Цена',
                                       widget=DividedRangeWidget(),
                                       )

    assembly = django_filters.BooleanFilter(field_name='id',
                                            label='В сборке',
                                            method='assembly_filter',
                                            widget=CheckboxInput(),
                                            )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None, product_group_id=None):
        super().__init__(data, queryset, request=request, prefix=prefix)

        disabled = not (request and request.user.is_authenticated)
        favourites = django_filters.BooleanFilter(field_name='favourites',
                                                  label='В избранном',
                                                  method=self.user_filter,
                                                  disabled=disabled,
                                                  widget=CheckboxInput(),
                                                  )

        self.filters['favourites'] = favourites
        subscriptions = django_filters.BooleanFilter(field_name='subscriptions',
                                                     label='В рассылке',
                                                     method=self.user_filter,
                                                     disabled=disabled,
                                                     widget=CheckboxInput(),
                                                     )

        self.filters['subscriptions'] = subscriptions

        if not product_group_id:
            try:
                # For DRF API Filtering in nested routes parameters form url are in parser_context
                product_group_id = request.parser_context['kwargs']['group_pk']
            except Exception:
                pass

        if product_group_id:
            for f in filter_by_group(product_group_id):
                new_filter = None
                if f.display_widget == 'CHOICE':
                    choices = ((item, item) for item in filter_choices(f.specification_id, product_group_id))
                    new_filter = SpecMultipleChoiceFilter(field_name='specifications__value',
                                                          choices=choices,
                                                          label=f.specification_name,
                                                          )
                elif f.display_widget == 'RANGE':
                    min_value, max_value = filter_max_and_min_values(f.specification_id, product_group_id)
                    new_filter = SpecRangeFilter(field_name='specifications__value_float',
                                                 label=f.specification_name,
                                                 widget=DividedRangeWidget(
                                                     placeholders=[f'от {min_value}', str(f'до {max_value}')]))

                if new_filter:
                    new_filter.set_extra_predicate(name='specifications__specification__filtering__filter_name',
                                                   value=f.filter_name)
                    self.filters[f.filter_name] = new_filter

    def user_filter(self, queryset, name, value):
        if value and self.request:
            user = getattr(self.request, 'user', None)
            if user.is_authenticated:
                return queryset.filter(**{
                    name: user,
                })
        else:
            return queryset

    def assembly_filter(self, queryset, name, value):
        if value and self.request:
            user_assembly = UserAssembly(self.request)
            name = f'{name}__in'

            value = (item['product'].id for item in user_assembly)
            return queryset.filter(**{
                name: value,
            })
        else:
            return queryset
