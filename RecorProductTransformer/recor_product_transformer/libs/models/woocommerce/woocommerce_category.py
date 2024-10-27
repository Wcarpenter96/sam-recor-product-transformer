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

    def to_json(self) -> dict:
        """
        Transforms a WooCommerce instance into json
        Returns:
            Dict[str, Any]: The json transformation
        """
        woocommerce_category = {
            "name": self.name,
            "slug": self.slug,
        }

        if self.parent:
            woocommerce_category["parent"] = int(self.parent)

        # For Updates Only
        if self.id:
            woocommerce_category["id"] = int(self.id)

        # For Creates Only
        if self.image:
            woocommerce_category["image"] = (self.image.to_json(),)

        return woocommerce_category
