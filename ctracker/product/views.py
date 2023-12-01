from collections import defaultdict

from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from .filters import ProductFilterSet
from .models import ProductGroup, Product, get_favourites_list, get_subscriptions_list, annotate_queryset_with_price
# from .forms import ProductFilterForm
from assembly.services import UserAssembly


class ProductGroupListView(ListView):
    model = ProductGroup
    context_object_name = 'product_groups'
    template_name = 'product/productgroup/list.html'


class ProductListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'product/product/list.html'
    paginate_by = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = None
        self.user_assembly = None
        self.filter_set = None

    def get_queryset(self):
        # TODO: Закинуть поле search в форму и отображать в template через группы (field group или fieldset).
        #   Добавить Search2 к полю search
        # TODO: Разбить список продуктов на отдельные файды (форма фильтра. карточку продукта).
        #   Карточку можно будет переиспользовать. Стр 82
        # TODO: |linebreaks forloop.counter |pluralize
        # TODO: django - autocomplete - light, django-ajax-selects
        try:
            self.group = get_object_or_404(ProductGroup, id=self.kwargs['id'])
        except KeyError:
            self.group = None

        self.user_assembly = UserAssembly(self.request)

        qs = super().get_queryset()

        if self.group:
            qs = qs.filter(group=self.group)

        qs = annotate_queryset_with_price(qs, '')

        f = ProductFilterSet(self.request.GET, qs,
                             request=self.request,
                             product_group_id=self.group.id if self.group else None)

        self.filter_set = f

        return f.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context['page_obj']
        paginator = context['paginator']
        if page is not None and paginator is not None:
            context['page_range'] = list(paginator.get_elided_page_range(page.number, on_each_side=4, on_ends=2))
        context['group'] = self.group

        context['filter_set'] = self.filter_set

        context['in_assembly_list'] = list((item['product'].id for item in self.user_assembly))
        if self.request.user.is_authenticated:
            context['in_favourites_list'] = get_favourites_list(self.request.user)
            context['in_subscriptions_list'] = get_subscriptions_list(self.request.user)

        context['search_value'] = self.filter_set.form.cleaned_data.get('search', '')

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product/detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('brand', 'group')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        specification_values = product.specifications.select_related('specification', 'specification__group').order_by(
            'specification__group__order',
            'specification__order')

        specdict = defaultdict(list)
        for specification_value in specification_values:
            specdict[specification_value.specification.group.name].append(
                (specification_value.specification.name, specification_value.value))
        specdict.default_factory = None  # Disable default factory to be able to iterate items in template

        prices = product.get_prices()

        context['specs'] = specdict
        context['prices'] = prices

        context['assembly'] = UserAssembly(self.request)

        return context
