from dataclasses import dataclass
from typing import List, Optional

from recor_product_transformer.libs.models.woocommerce.woocommerce_category import (
    WooCommerceCategory,
)
from recor_product_transformer.libs.models.woocommerce.woocommerce_dimensions import (
    WooCommerceDimensions,
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
    dimensions: Optional[List[WooCommerceDimensions]] = None
    categories: Optional[List[WooCommerceCategory]] = None
    images: Optional[List[WooCommerceImage]] = None

    def to_json(self) -> dict:
        """
        Transforms a WooCommerce instance into json
        Returns:
            Dict[str, Any]: The json transformation
        """
        return {
            "type": self.type,
            "id": self.id,
            "slug": self.slug,
            "sku": self.sku,
            "name": self.name,
            "regular_price": self.regular_price,
            "stock_quantity": self.stock_quantity,
            "description": self.description,
            "categories": [category.to_json() for category in self.categories],
            "images": [image.to_json() for image in self.images],
        }
