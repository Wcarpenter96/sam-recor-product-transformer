import os
from typing import cast

from recor_product_getter.libs.requests.woocommerce.woocommerce_base_request import (
    WooCommerceBaseRequest,
)


class WooCommerceGetCounterRequest(WooCommerceBaseRequest):
    def run(self) -> dict:
        iml_counter_product_id = os.getenv("WOOCOMMERCE_IML_COUNTER_PRODUCT_ID")
        response = self.client.get(f"products/{iml_counter_product_id}")
        if response.ok:
            counter = response.json()["stock_quantity"]
            return cast(int, counter)
        else:
            raise Exception(response.text)
