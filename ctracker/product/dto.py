# Data Transfer Objects for Product app
from typing import NamedTuple


class ProductDTO(NamedTuple):
    vendor_name: str
    product_external_id: str
    name: str
    specs: str
    description: str
    image_link: str
    url: str
    price: float
    spec_list: list
    brand: str
