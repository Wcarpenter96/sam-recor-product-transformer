from dataclasses import dataclass
from typing import List, Optional

from recor_product_transformer.libs.models.woocommerce.woocommerce_category import (
    WooCommerceCategory,
)
from recor_product_transformer.libs.models.woocommerce.woocommerce_image import (
    WooCommerceImage,
)


@dataclass(frozen=True)
class WooCommerceProduct:
    """
    Object that holds the attributes and data required for a Woocommerce product
    """

    type: str = "simple"
    id: Optional[int] = None
    slug: Optional[str] = None
    sku: Optional[str] = None
    name: Optional[str] = None
    regular_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    description: Optional[str] = None
    categories: Optional[List[WooCommerceCategory]] = None
    images: Optional[List[WooCommerceImage]] = None
