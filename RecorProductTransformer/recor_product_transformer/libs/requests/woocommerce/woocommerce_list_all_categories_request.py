from typing import List, Optional, cast

from recor_product_transformer.libs.requests.woocommerce.woocommerce_base_request import (
    WooCommerceBaseRequest,
)


class WooCommerceListAllCategoriesRequest(WooCommerceBaseRequest):
    def run(self, ids: Optional[List[str]]) -> dict:

        params = {"per_page": 100}
        if ids is not None:
            params = params | {"include": ids}

        print(f"ATTEMPT: Getting WooCommerce Categories with params: {params}")
        response = self.client.get("products/categories", params=params)

        if response.ok:
            print(f"SUCCESS: Received WooCommerce Categories", response.json())
            return cast(dict, response.json())
        else:
            raise Exception(response.text)
