from typing import cast

from recor_product_transformer.libs.requests.woocommerce.woocommerce_base_request import (
    WooCommerceBaseRequest,
)


class WooCommerceListAllProductsRequest(WooCommerceBaseRequest):
    def run(self) -> dict:
        response = self.client.get("products", params={"per_page": 100})
        if response.ok:
            return cast(dict, response.json())
        else:
            raise Exception(response.text)
