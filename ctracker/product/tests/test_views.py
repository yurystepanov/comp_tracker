from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from datetime import date
from django.contrib.auth import get_user_model

from product.models import (ProductGroup, Product, Brand, SpecificationGroup, Specification, SpecificationValue,
                            ProductFilter)

from vendor.models import Vendor, VendorPrice


class ProductGroupListView(TestCase):
    number_of_groups = 10

    @classmethod
    def setUpTestData(cls):
        # Create product groups
        for group_id in range(cls.number_of_groups):
            ProductGroup.objects.create(
                name=f'Product group {group_id}',
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('product:product_group_list'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('product:product_group_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/productgroup/list.html')

    def test_lists_all_groups(self):
        response = self.client.get(reverse('product:product_group_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['product_groups']), self.number_of_groups)


def generate_data():
    number_of_products = 15
    user_model = get_user_model()
    user_model.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

    # Create product groups
    group1 = ProductGroup.objects.create(name='NoPriceGroup')
    group2 = ProductGroup.objects.create(name='PriceGroup')
    vendor = Vendor.objects.create(name='VENDOR')
    specification_group = SpecificationGroup.objects.create(name='SpecGroup1')
    specification = Specification.objects.create(group=specification_group,
                                                 name='Spec1'
                                                 )

    product_filter = ProductFilter.objects.create(group=group2,
                                                  specification=specification,
                                                  filter_name='released'
                                                  )

    # product_filter_value = ProductFilterValue.objects.create(filter=product_filter,
    #                                                          value='4023')
    # product_filter_value = ProductFilterValue.objects.create(filter=product_filter,
    #                                                          value='2023')

    for product_id in range(number_of_products):
        Product.objects.create(
            name=f'Product group{product_id}',
            brand=Brand.objects.create(name=f'Brand1{product_id}'),
            group=group1
        )
    for product_id in range(number_of_products):
        product = Product.objects.create(
            name=f'Product group{product_id}',
            brand=Brand.objects.create(name=f'Brand2{product_id}'),
            group=group2
        )

        price = VendorPrice.objects.create(vendor=vendor,
                                           product=product,
                                           price=(product_id + 1) * 200,
                                           date=date.today(),
                                           )

        # print(price)

        SpecificationValue.objects.create(product=product,
                                          specification=specification,
                                          value=str(2020 + product_id))


class ProductListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        generate_data()

    def products_test_base(self, parameters='', status_code=200, login=False):
        group1 = ProductGroup.objects.filter(name='PriceGroup')[0]

        if login:
            self.client.login(username='temporary', password='temporary')
        response = self.client.get(reverse('product:product_list_by_id', kwargs={'id': group1.id}) + parameters)
        self.assertEqual(response.status_code, status_code)

        return response

    def test_view_url_exists_at_desired_location(self):
        group1 = ProductGroup.objects.all().first()
        response = self.client.get(f'/product/group/{group1.id}/')
        self.assertEqual(response.status_code, 200)

    def test_view_404_on_not_exist(self):
        group1 = ProductGroup.objects.all().first()
        response = self.client.get(f'/product/group/1234567/')
        self.assertEqual(response.status_code, 404)

    def test_view_url_accessible_by_name_id_slug(self):
        group1 = ProductGroup.objects.all().first()
        response = self.client.get(reverse('product:product_list', kwargs={'id': group1.id, 'slug': group1.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name_id(self):
        self.products_test_base()

    def test_view_uses_correct_template(self):
        response = self.products_test_base()
        self.assertTemplateUsed(response, 'product/product/list.html')

    def test_lists_no_price(self):
        group1 = ProductGroup.objects.filter(name='NoPriceGroup')[0]
        response = self.client.get(reverse('product:product_list_by_id', kwargs={'id': group1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 0)

    def test_lists_all_products(self):
        response = self.products_test_base()
        # pagination = 10
        self.assertEqual(len(response.context['products']), 10)

    def test_lists_2nd_page(self):
        response = self.products_test_base(parameters='?page=2')
        self.assertEqual(len(response.context['products']), 5)

    def test_list_not_existing_page(self):
        self.products_test_base(parameters='?page=3', status_code=404)

    def test_search(self):
        response = self.products_test_base(parameters='?search=group1')
        self.assertEqual(len(response.context['products']), 6)

    def test_assembly_no_login(self):
        response = self.products_test_base(parameters='?assembly=on')
        self.assertEqual(len(response.context['products']), 0)

    def test_assembly_login(self):
        response = self.products_test_base(parameters='?assembly=on', login=True)
        self.assertEqual(len(response.context['products']), 0)

    def test_favourites_no_login(self):
        response = self.products_test_base(parameters='?favourites=on')
        self.assertEqual(len(response.context['products']), 10)

    def test_favourites_login(self):
        response = self.products_test_base(parameters='?favourites=on', login=True)
        self.assertEqual(len(response.context['products']), 0)

    def test_price(self):
        response = self.products_test_base(parameters='?price_from=1000&price_to=2000')
        self.assertEqual(len(response.context['products']), 6)

    def test_brand(self):
        response = self.products_test_base(parameters='?brand=Brand22')
        self.assertEqual(len(response.context['products']), 1)

    def test_specs_filter_not_exists(self):
        self.assertRaises(ValueError, self.products_test_base, parameters='?released=4023')

    def test_specs_filter_exists(self):
        response = self.products_test_base(parameters='?released=2023')
        self.assertEqual(len(response.context['products']), 1)


class ProductDetailView(TestCase):
    number_of_products = 15

    @classmethod
    def setUpTestData(cls):
        # Create product groups
        group = ProductGroup.objects.create(name='PriceGroup')
        vendor = Vendor.objects.create(name='VENDOR')

        for product_id in range(cls.number_of_products):
            product = Product.objects.create(
                name=f'Product group{product_id}',
                brand=Brand.objects.create(name=f'Brand2{product_id}'),
                group=group
            )

            VendorPrice.objects.create(vendor=vendor,
                                       product=product,
                                       price=(product_id + 1) * 200,
                                       date=date.today()
                                       )

    def test_view_url_exists_at_desired_location(self):
        product = Product.objects.all().first()
        response = self.client.get(f'/product/{product.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_id(self):
        product = Product.objects.all().first()
        response = self.client.get(reverse('product:product_detail_by_id', kwargs={'pk': product.pk}))
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_id_slug(self):
        product = Product.objects.all().first()
        response = self.client.get(reverse('product:product_detail', kwargs={'pk': product.pk,
                                                                             'slug': product.slug}))
        self.assertEqual(response.status_code, 200)

    @override_settings(CACHES=getattr(settings, 'TEST_CACHES'))
    def test_view_uses_correct_template(self):
        product = Product.objects.all().first()
        response = self.client.get(reverse('product:product_detail', kwargs={'pk': product.pk,
                                                                             'slug': product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/product/detail.html')

    def test_not_existing_product(self):
        response = self.client.get(reverse('product:product_detail_by_id', kwargs={'pk': '1234567'}))
        self.assertEqual(response.status_code, 404)

    @override_settings(CACHES=getattr(settings, 'TEST_CACHES'))
    def test_view__has_product(self):
        product = Product.objects.all().first()
        response = self.client.get(reverse('product:product_detail', kwargs={'pk': product.pk,
                                                                             'slug': product.slug}))

        product = response.context.get('product')
        self.assertIsNotNone(product)

    @override_settings(CACHES=getattr(settings, 'TEST_CACHES'))
    def test_view_has_price(self):
        product = Product.objects.all().first()
        response = self.client.get(reverse('product:product_detail', kwargs={'pk': product.pk,
                                                                             'slug': product.slug}))

        product = response.context['product']
        self.assertEquals(product.price(), product.id * 200)


class AddToFavourites(TestCase):
    @classmethod
    def setUpTestData(cls):
        generate_data()

    def test_add_to_favourites(self):
        pass

    def test_add_to_favourites(self):
        pass
