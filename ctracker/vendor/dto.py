# Data Transfer Objects for Vendor app

from typing import NamedTuple
from datetime import date


class PriceDTO(NamedTuple):
    vendor_name: str
    product_external_id: str
    price: float
    from_date: date
