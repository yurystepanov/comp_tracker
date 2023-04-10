from django.test import TestCase
from product.forms import ProductFilterForm
from mock import patch


class ProductFilterFormTests(TestCase):
    group = '1'

    def test_empty_form(self):
        form = ProductFilterForm(group=self.group, data={})
        self.assertEqual(form.is_valid(), True)

    def test_field_price_from_good(self):
        form = ProductFilterForm(group=self.group, data={'price_from': '1000'})
        self.assertEqual(form.is_valid(), True)

    def test_field_price_from_bad(self):
        form = ProductFilterForm(group=self.group, data={'price_from': '1d000'})
        self.assertEqual(form.errors['price_from'], ['Enter a whole number.'])

    def test_field_price_to_good(self):
        form = ProductFilterForm(group=self.group, data={'price_to': '1000'})
        self.assertEqual(form.is_valid(), True)

    def test_field_price_to_bad(self):
        form = ProductFilterForm(group=self.group, data={'price_to': '1d000'})
        self.assertEqual(form.errors['price_to'], ['Enter a whole number.'])

    def test_field_brand_exists(self):
        form = ProductFilterForm(group=self.group, data={'brand': 'Intel'})
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['brand'], 'Intel')

    def test_field_favourites_on_authenticated(self):
        form = ProductFilterForm(group=self.group, is_authenticated=True, data={'favourites': 'on'})
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['favourites'], True)

    def test_field_favourites_not_authenticated(self):
        form = ProductFilterForm(group=self.group, data={'favourites': 'on'})
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['favourites'], False)

    def test_field_favourites_off(self):
        form = ProductFilterForm(group=self.group, data={'favourites': ''})
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['favourites'], False)

    def test_field_assembly_on(self):
        form = ProductFilterForm(group=self.group, data={'assembly': 'on'})
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['assembly'], True)

    def test_field_assembly_off(self):
        form = ProductFilterForm(group=self.group, data={'assembly': ''})
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['assembly'], False)

    def test_filter_fields_good(self):
        with patch('product.forms.make_product_group_spec_queryset') as filters:
            filters_return = [{'value': f'2{i}0v'} for i in range(5)]

            filters.return_value = [[['vlt', 'voltage'], filters_return]]

            form = ProductFilterForm(group=self.group, data={'vlt': ['220v', '240v']})
            filters.assert_called_once()
            self.assertEqual(form.is_valid(), True)
            self.assertEqual(form.cleaned_data['vlt'], ['220v', '240v'])

    def test_filter_fields_bad(self):
        with patch('product.forms.make_product_group_spec_queryset') as filters:
            filters_return = [{'value': f'2{i}0v'} for i in range(5)]
            filters.return_value = [[['vlt', 'voltage'], filters_return]]

            form = ProductFilterForm(group=self.group, data={'vlt': ['220v', '2400v']})
            filters.assert_called_once()
            self.assertEqual(form.is_valid(), False)
            self.assertEqual(form.errors['vlt'], ['Select a valid choice. 2400v is not one of the available choices.'])
