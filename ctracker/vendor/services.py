from django.contrib.contenttypes.models import ContentType

from .dto import PriceDTO
from .models import Vendor, VendorPrice, VendorLink


def create_vendor_link(vendor_or_id, external_id, target, url):
    """
    Links target object with vendor by creating VendorLink object

    Parameters: vendor_or_id - Vendor object or vendor_id,
                external_id - object id in Vendor's system,
                url- link to object on Vendor's site

    Returns: VendorLink object
    """
    vendor_link = VendorLink.objects.create(vendor=vendor_obj(vendor_or_id),
                                            external_id=external_id,
                                            target=target,
                                            url=url
                                            )

    return vendor_link


def product_exists(vendor_or_id, product_external_id):
    """
    Checks if VendorLink exists for product object

    Parameters: vendor_or_id - Vendor object or vendor_id,
                product_external_id - product id in Vendor's system,

    Returns: True if exists otherwise False
    """
    product_content_type = ContentType.objects.get_by_natural_key(app_label='product', model='product')

    return vendor_link_exists(vendor_or_id, product_external_id, product_content_type)


def vendor_link_exists(vendor_or_id, external_id, content_type):
    """
    Checks if VendorLink exists for object

    Parameters: vendor_or_id - Vendor object or vendor_id,
                external_id  - object id in Vendor's system,
                content_type - ContentType of object

    Returns: True if exists otherwise False
    """
    return VendorLink.objects.filter(vendor=vendor_obj(vendor_or_id),
                                     external_id=external_id,
                                     target_ct=content_type
                                     ).exists()


def vendor_name_to_id(name):
    """
    Returns vendor.id by vendor.name Throws exception in no Vendor by name found
    """
    vendor = Vendor.objects.get(name=name)
    return vendor.id


def vendor_obj(vendor_or_id):
    """
    Returns Vendor object. Helper function for other functions to have 'polymorphic' implementation
    Parameters: vendor_or_id could be Vendor or Vendor.id.
    """
    if type(vendor_or_id) is int:
        vendor = Vendor.objects.get(id=vendor_or_id)
    else:
        vendor = vendor_or_id

    return vendor


def get_external_id_by_object(obj, vendor_or_id):
    """
    Returns external_id for vendor and object from parameters
    Parameters: obj - linked object, vendor_or_id could be Vendor or Vendor.id.
    """
    content_type = ContentType.objects.get_for_model(obj.__class__)

    vendor_link = VendorLink.objects.filter(vendor=vendor_obj(vendor_or_id),
                                            target_id=obj.id,
                                            target_ct=content_type
                                            ).first()

    return vendor_link.external_id if vendor_link else ''


def get_external_ids_by_object(obj, vendor_or_id=None):
    """
    Returns external_id's for vendor and object from parameters
    Parameters: obj - linked object, vendor_or_id could be Vendor or Vendor.id.
    """
    content_type = ContentType.objects.get_for_model(obj.__class__)
    vendor_links = VendorLink.objects.filter(vendor=vendor_obj(vendor_or_id),
                                             target_id=obj.id,
                                             target_ct=content_type
                                             )

    return (vendor_link.external_id for vendor_link in vendor_links)


def get_object_by_external_id(vendor_or_id, external_id, content_type):
    """
    Returns object by external_id, vendor and object content type from parameters
    """
    vendor_link = VendorLink.objects.get(vendor=vendor_obj(vendor_or_id),
                                         external_id=external_id,
                                         target_ct=content_type
                                         )

    obj = content_type.get_object_for_this_type(id=vendor_link.target_id)
    return obj


def set_price_from_dto(price_dto: PriceDTO) -> VendorPrice:
    """
    Creates or Updates vendor price using data from price data transfer object
    Returns: VendorPrice object
    """
    product_content_type = ContentType.objects.get_by_natural_key(app_label='product', model='product')
    vendor = Vendor.objects.get(name=price_dto.vendor_name)

    product = get_object_by_external_id(vendor,
                                        price_dto.product_external_id,
                                        product_content_type)

    price = VendorPrice.objects.update_or_create(vendor=vendor,
                                                 product=product,
                                                 date=price_dto.from_date,
                                                 defaults={'price': price_dto.price},
                                                 )
    return price
