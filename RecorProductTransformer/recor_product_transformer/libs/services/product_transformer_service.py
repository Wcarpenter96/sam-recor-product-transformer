from typing import Dict

from recor_product_transformer.libs.requests.iml.iml_get_category_list_request import (
    ImlGetCategoryListRequest,
)
from recor_product_transformer.libs.requests.woocommerce.woocommerce_batch_update_categories_request import (
    WooCommerceBatchUpdateCategoriesRequest,
)
from recor_product_transformer.libs.requests.woocommerce.woocommerce_list_all_categories_request import (
    WooCommerceListAllCategoriesRequest,
)
from recor_product_transformer.libs.transformers.iml.iml_category_transformer import (
    ImlCategoryTransformer,
)
from recor_product_transformer.libs.transformers.iml.iml_item_transformer import (
    ImlItemTransformer,
)


class ProductTransformerService:
    def __init__(self):
        self.woocommerce_batch_update_categories_request = (
            WooCommerceBatchUpdateCategoriesRequest
        )
        self.woocommerce_list_all_product_categories_request = (
            WooCommerceListAllCategoriesRequest()
        )
        self.iml_get_category_list_request = ImlGetCategoryListRequest()
        self.iml_item_transformer = ImlItemTransformer()
        self.iml_category_transformer = ImlCategoryTransformer()

    def run(self, products) -> Dict:
        print(products)
        iml_category_ids = {
            category_id
            for product in products
            for category_id in product["category_id"]
        }
        categories = self.woocommerce_list_all_product_categories_request.run()
        category_id_map = {category["slug"]: category["id"] for category in categories}

        # Create new categories
        # TODO Create parent categories
        new_category_ids = iml_category_ids - category_id_map.keys()
        if new_category_ids:
            new_categories = []
            iml_categories = self.iml_get_category_list_request.run()
            for category_id in new_category_ids:
                iml_category = [
                    iml_category
                    for iml_categories in iml_categories
                    if iml_categories["short_code"] == category_id
                ]
                category = self.iml_category_transformer.run(iml_category)
                new_categories.append(category)
            self.woocommerce_batch_update_categories_request.run(new_categories)

        # TODO Create new products
        return {}
