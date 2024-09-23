from typing import Dict

from recor_product_transformer.libs.models.woocommerce import woocommerce_category
from recor_product_transformer.libs.requests.iml.iml_get_category_list_request import (
    ImlGetCategoryListRequest,
)
from recor_product_transformer.libs.requests.woocommerce.woocommerce_batch_update_categories_request import (
    WooCommerceBatchUpdateCategoriesRequest,
)
from recor_product_transformer.libs.requests.woocommerce.woocommerce_batch_update_products_request import \
    WooCommerceBatchUpdateProductsRequest
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
            WooCommerceBatchUpdateCategoriesRequest()
        )
        self.woocommerce_batch_update_products_request = WooCommerceBatchUpdateProductsRequest()
        self.woocommerce_list_all_product_categories_request = (
            WooCommerceListAllCategoriesRequest()
        )
        self.iml_get_category_list_request = ImlGetCategoryListRequest()
        self.iml_item_transformer = ImlItemTransformer()
        self.iml_category_transformer = ImlCategoryTransformer()

    def run(self, products) -> Dict:
        iml_category_ids = {
            category_id
            for product in products
            for category_id in product["category_id"]
        }
        woocommerce_categories = self.woocommerce_list_all_product_categories_request.run(slug=None)
        woocommerce_categories_by_slug = {category["slug"]: category for category in woocommerce_categories}

        # Create new categories
        # TODO Create parent categories
        new_category_ids = iml_category_ids - woocommerce_categories_by_slug.keys()
        if new_category_ids:
            new_categories = []
            all_iml_categories = self.iml_get_category_list_request.run()
            new_iml_categories = [
                iml_category
                for iml_category in all_iml_categories
                if iml_category["category_id"] in new_category_ids
            ]
            for new_iml_category in new_iml_categories:
                new_woocommerce_category = self.iml_category_transformer.transform(new_iml_category)
                new_categories.append(new_woocommerce_category)
            self.woocommerce_batch_update_categories_request.run(new_categories)

        # Create new products
        new_woocommerce_products = [
            self.iml_item_transformer.transform({**product, ImlItemTransformer.WOOCOMMERCE_CATEGORIES_BY_SLUG: woocommerce_categories_by_slug }) for
            product in products]
        self.woocommerce_batch_update_products_request.run(new_woocommerce_products)

        return {}
