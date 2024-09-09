from dataclasses import dataclass
from typing import Optional

from recor_product_transformer.libs.models.woocommerce.woocommerce_image import (
    WooCommerceImage,
)


@dataclass(frozen=True)
class WooCommerceCategory:
    """
    Object that holds the attributes and data required for a Woocommerce category
    """

    id: Optional[int] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    parent: Optional[int] = None
    image: Optional[WooCommerceImage] = None
