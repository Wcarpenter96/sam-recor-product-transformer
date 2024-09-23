from typing import Optional, cast

from recor_product_transformer.libs.requests.woocommerce.woocommerce_base_request import (
    WooCommerceBaseRequest,
)


class WooCommerceListAllProductsRequest(WooCommerceBaseRequest):
    def run(self, slug: Optional[str]) -> dict:
        if slug is not None:
            params = {"slug": slug}
        else:
            params = {"per_page": 100}
        response = self.client.get("products", params=params)
        if response.ok:
            return cast(dict, response.json())
        else:
            raise Exception(response.text)

    def run(self, slug: Optional[str]) -> dict:

        print(f"ATTEMPT: Getting WooCommerce Products with slug: {slug}")

        if slug is not None:
            params = {"slug": slug}
        else:
            params = {"per_page": 100}
        response = self.client.get("products", params=params)

        if response.ok:
            print(f"SUCCESS: Received WooCommerce Products", response.json())
            return cast(dict, response.json())
        else:
            raise Exception(response.text)

