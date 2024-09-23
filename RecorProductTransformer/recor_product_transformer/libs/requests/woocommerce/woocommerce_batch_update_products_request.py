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

    def run(self, products: List[WooCommerceProduct]) -> dict:

        products_json = [product.to_json() for product in products]

        print("ATTEMPT: Batch Updating WooCommerce Products:", products_json)

        response = self.client.post(
            "products/batch", {"create": products_json}
        )

        if response.ok:
            print("SUCCESS: Updated WooCommerce Products:", response.json())
            return cast(dict, response.json())
        else:
            raise Exception(response.text)
