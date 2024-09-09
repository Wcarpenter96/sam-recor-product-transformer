from typing import List, cast

from recor_product_transformer.libs.models.woocommerce.woocommerce_category import (
    WooCommerceCategory,
)
from recor_product_transformer.libs.requests.woocommerce.woocommerce_base_request import (
    WooCommerceBaseRequest,
)


class WooCommerceBatchUpdateCategoriesRequest(WooCommerceBaseRequest):
    """
    By default, it's limited to up to 100 objects to be created, updated or deleted.
    """

    def run(self, categories: List[WooCommerceCategory]) -> dict:
        response = self.client.put(
            "products/categories/batch", {"create": categories.to_json()}
        )
        if response.ok:
            return cast(dict, response.json())
        else:
            raise Exception(response.text)
