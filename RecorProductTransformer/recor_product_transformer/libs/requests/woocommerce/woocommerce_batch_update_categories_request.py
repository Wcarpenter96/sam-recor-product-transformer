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

        categories_json = [category.to_json() for category in categories]

        print("ATTEMPT: Batch Updating WooCommerce Categories:", categories_json)

        response = self.client.post(
            "products/categories/batch", {"create": categories_json}
        )

        if response.ok:
            # TODO: Handle Create/Update Failures
            print("SUCCESS: Updated WooCommerce Categories:", response.json())
            return cast(dict, response.json())
        else:
            raise Exception(response.text)
