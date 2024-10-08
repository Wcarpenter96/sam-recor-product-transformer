from typing import List, Optional, cast

from recor_product_transformer.libs.requests.woocommerce.woocommerce_base_request import (
    WooCommerceBaseRequest,
)


class WooCommerceListAllProductsRequest(WooCommerceBaseRequest):
    def run(self, ids: Optional[List[str]]) -> dict:

        params = {"per_page": 100}
        if ids is not None:
            params = params | {"include": ids}

        print(f"ATTEMPT: Getting WooCommerce Products with params: {params}")
        response = self.client.get("products", params=params)

        if response.ok:
            print(f"SUCCESS: Received WooCommerce Products", response.json())
            return cast(dict, response.json())
        else:
            raise Exception(response.text)
