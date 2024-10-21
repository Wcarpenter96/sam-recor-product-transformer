from typing import List, cast

from recor_product_transformer.libs.models.woocommerce.woocommerce_product import (
    WooCommerceProduct,
)
from recor_product_transformer.libs.requests.woocommerce.woocommerce_base_request import (
    WooCommerceBaseRequest,
)


class WooCommerceBatchUpdateProductsRequest(WooCommerceBaseRequest):
    """
    By default, it's limited to up to 100 objects to be created, updated or deleted.
    """

    def run(
        self,
        new_products: List[WooCommerceProduct],
        old_products: List[WooCommerceProduct],
    ) -> dict:

        products_json = {
            "create": [product.to_json() for product in new_products],
            "update": [product.to_json() for product in old_products],
        }

        print("ATTEMPT: Batch Updating WooCommerce Products:", products_json)

        response = self.client.post("products/batch", products_json)

        if response.ok:
            # TODO: Handle Create/Update Failures
            print("SUCCESS: Updated WooCommerce Products:", response.json())
            return cast(dict, response.json())
        else:
            raise Exception(response.text)
