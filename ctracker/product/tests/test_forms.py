# import mock
from django.test import TestCase
# from product.forms import ProductFilterForm
from product.filters import ProductFilterSet
from product.models import ProductGroup, Product


# from mock import patch


class ProductFilterFormTests(TestCase):
    group = ProductGroup.objects.get(id=1)
    qs = Product.objects.all()
    group_id = 1

    def _getForm(self, data=None, is_authenticated=False):
        class MockUser:
            is_authenticated = True

        class MockRequest:
            user = MockUser()

        request = None
        if is_authenticated:
            request = MockRequest()
        filter_set = ProductFilterSet(queryset=self.qs, product_group_id=self.group_id, data=data, request=request)
        return filter_set.form

    def test_empty_form(self):
        data = {}
        form = self._getForm(data=data)
        self.assertEqual(form.is_valid(), True)

    def test_field_price_from_good(self):
        data = {'price_min': '1000'}
        form = self._getForm(data=data)
        self.assertEqual(form.is_valid(), True)

    def test_field_price_from_bad(self):
        data = {'price_min': '1d000'}
        form = self._getForm(data=data)

        self.assertEqual(form.errors['price'], ['Введите число.'])

    def test_field_price_to_good(self):
        data = {'price_max': '1000'}
        form = self._getForm(data=data)
        self.assertEqual(form.is_valid(), True)

    def test_field_price_to_bad(self):
        data = {'price_max': '1d000'}
        form = self._getForm(data=data)

        self.assertEqual(form.errors['price'], ['Введите число.'])

    def test_field_brand_exists(self):
        data = {'brand': 'Intel'}
        form = self._getForm(data=data)
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['brand'], 'Intel')

    def test_field_favourites_on_authenticated(self):
        data = {'favourites': 'on'}
        form = self._getForm(data=data, is_authenticated=True)
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['favourites'], True)

    def test_field_favourites_not_authenticated(self):
        data = {'favourites': 'on'}
        form = self._getForm(data=data, is_authenticated=False)
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['favourites'], None)

    def test_field_favourites_off(self):
        data = {'favourites': ''}
        form = self._getForm(data=data, is_authenticated=True)
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['favourites'], False)

    def test_field_assembly_on(self):
        data = {'assembly': 'on'}
        form = self._getForm(data=data)
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['assembly'], True)

    def test_field_assembly_off(self):
        data = {'assembly': ''}
        form = self._getForm(data=data)
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['assembly'], False)

    # def test_filter_fields_good(self):
    #     with patch('product.forms.make_product_group_spec_queryset') as filters:
    #         filters_return = [{'value': f'2{i}0v'} for i in range(5)]
    #
    #         filters.return_value = [[['vlt', 'voltage'], filters_return]]
    #
    #         form = ProductFilterForm(group=self.group, data={'vlt': ['220v', '240v']})
    #         filters.assert_called_once()
    #         self.assertEqual(form.is_valid(), True)
    #         self.assertEqual(form.cleaned_data['vlt'], ['220v', '240v'])
    #
    # def test_filter_fields_bad(self):
    #     with patch('product.forms.make_product_group_spec_queryset') as filters:
    #         filters_return = [{'value': f'2{i}0v'} for i in range(5)]
    #         filters.return_value = [[['vlt', 'voltage'], filters_return]]
    #
    #         form = ProductFilterForm(group=self.group, data={'vlt': ['220v', '2400v']})
    #         filters.assert_called_once()
    #         self.assertEqual(form.is_valid(), False)
    #         self.assertEqual(form.errors['vlt'], ['Выберите корректный вариант. 2400v нет среди допустимых значений.'])
