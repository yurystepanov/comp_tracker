from collections import defaultdict

from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from .models import ProductGroup, Product, get_favourites_list, get_subscriptions_list, annotate_queryset_with_price
from .forms import ProductFilterForm
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
        self.form = None
        self.search_value = ''
        self.group = None
        self.user_assembly = None

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

        reserved_filters = {'page', 'search'}

        qs = super().get_queryset()

        if self.group:
            qs = qs.filter(group=self.group)

        qs = annotate_queryset_with_price(qs, '')

        form = ProductFilterForm(group=self.group,
                                 is_authenticated=self.request.user.is_authenticated,
                                 data=self.request.GET)
        if not form.is_valid():
            raise ValueError(form.errors)

        filters = {'brand': 'brand__name__icontains',
                   'price_from': 'price__gte',
                   'price_to': 'price__lte',
                   }

        for key in form.cleaned_data:
            if key not in reserved_filters:
                value = form.cleaned_data[key]
                if value:
                    if key in filters:
                        qs = qs.filter(**{filters[key]: value})
                    elif key == 'favourites':
                        if self.request.user.is_authenticated:
                            qs = qs.filter(favourites=self.request.user)
                    elif key == 'subscriptions':
                        if self.request.user.is_authenticated:
                            qs = qs.filter(subscriptions=self.request.user)
                    elif key == 'assembly':
                        qs = qs.filter(id__in=list((item['product'].id for item in self.user_assembly)))
                    else:

                        qs = qs.filter(specifications__specification__filtering__filter_name=key,
                                       specifications__value__in=value)

        data = self.request.GET
        search_value = data.get('search', default=None)

        if search_value:
            qs = qs.filter(name__icontains=search_value)
            self.search_value = search_value

        self.form = form

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context['page_obj']
        paginator = context['paginator']
        if page is not None and paginator is not None:
            context['page_range'] = list(paginator.get_elided_page_range(page.number, on_each_side=4, on_ends=2))
        context['group'] = self.group

        context['form'] = self.form

        context['in_assembly_list'] = list((item['product'].id for item in self.user_assembly))
        if self.request.user.is_authenticated:
            context['in_favourites_list'] = get_favourites_list(self.request.user)
            context['in_subscriptions_list'] = get_subscriptions_list(self.request.user)

        context['search_value'] = self.search_value

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
