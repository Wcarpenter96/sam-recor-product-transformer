from typing import cast

from recor_product_transformer.libs.requests.woocommerce.woocommerce_base_request import (
    WooCommerceBaseRequest,
)


class WooCommerceBatchUpdateProductsRequest(WooCommerceBaseRequest):
    """
    By default, it's limited to up to 100 objects to be created, updated or deleted.
    """

    def run(self) -> dict:
        response = self.client.put("products", params={"per_page": 100})
        if response.ok:
            return cast(dict, response.json())
        else:
            raise Exception(response.text)
