from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from .models import Product, Brand, ProductGroup, SpecificationGroup, Specification, SpecificationValue
from .dto import ProductDTO
from vendor.services import (product_exists, get_object_by_external_id, set_price_from_dto,
                             create_vendor_link, vendor_name_to_id)
from vendor.dto import PriceDTO


def create_or_update_product(product_dto: ProductDTO, product_group: ProductGroup, overwrite_if_exists=False):
    new_product = False
    vendor_id = vendor_name_to_id(product_dto.vendor_name)
    if product_exists(vendor_id, product_dto.product_external_id):
        if overwrite_if_exists:
            product = get_object_by_external_id(vendor_or_id=vendor_id,
                                                external_id=product_dto.product_external_id,
                                                content_type=ContentType.objects.get_for_model(Product))
        else:
            return
    else:
        product = Product()
        new_product = True

    with transaction.atomic():
        product_brand = Brand.objects.get_or_create(name=product_dto.brand)[0]

        product.name = product_dto.name
        product.description_short = product_dto.specs
        product.description = product_dto.description
        product.group = product_group
        product.imageURL = product_dto.image_link
        product.brand = product_brand
        product.save()

        for group_title, spec_title, spec_value in product_dto.spec_list:
            product_spec_group = SpecificationGroup.objects.get_or_create(name=group_title)[0]
            specification = Specification.objects.get_or_create(name=spec_title, group=product_spec_group)[0]

            SpecificationValue.objects.get_or_create(product=product,
                                                     specification=specification,
                                                     defaults={'value': spec_value, }
                                                     )

        if new_product:
            create_vendor_link(vendor_or_id=vendor_id,
                               external_id=product_dto.product_external_id,
                               target=product,
                               url=product_dto.url
                               )

        price_dto = PriceDTO(vendor_name=product_dto.vendor_name,
                             product_external_id=product_dto.product_external_id,
                             price=product_dto.price,
                             from_date=date.today()
                             )

        set_price_from_dto(price_dto)
