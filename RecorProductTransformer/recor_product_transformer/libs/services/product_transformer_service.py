from typing import Dict

import boto3
from recor_product_transformer.libs.requests.iml.iml_get_category_list_request import (
    ImlGetCategoryListRequest,
)
from recor_product_transformer.libs.requests.woocommerce.woocommerce_batch_update_categories_request import (
    WooCommerceBatchUpdateCategoriesRequest,
)
from recor_product_transformer.libs.requests.woocommerce.woocommerce_batch_update_products_request import (
    WooCommerceBatchUpdateProductsRequest,
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
            WooCommerceBatchUpdateCategoriesRequest()
        )
        self.woocommerce_batch_update_products_request = (
            WooCommerceBatchUpdateProductsRequest()
        )
        self.woocommerce_list_all_product_categories_request = (
            WooCommerceListAllCategoriesRequest()
        )
        self.iml_get_category_list_request = ImlGetCategoryListRequest()
        self.iml_item_transformer = ImlItemTransformer()
        self.iml_category_transformer = ImlCategoryTransformer()
        self.dynamodb = boto3.resource("dynamodb")
        self.item_id_table = boto3.resource("dynamodb").Table("iml-item-id-table")
        self.category_id_table = boto3.resource("dynamodb").Table(
            "iml-category-id-table"
        )

    def run(self, products):
        iml_category_ids = {
            category_id
            for product in products
            for category_id in product["category_id"]
        }

        # Identify Existing IML Categories
        response = self.dynamodb.batch_get_item(
            RequestItems={
                "iml-category-id-table": {
                    "Keys": [
                        {"category_id": str(category_id)}
                        for category_id in iml_category_ids
                    ]
                }
            }
        )
        old_category_maps = [
            category
            for category in response.get("Responses", {}).get("category_id", [])
        ]
        old_iml_category_ids = {
            category["category_id"] for category in old_category_maps
        }
        new_iml_category_ids = iml_category_ids - old_iml_category_ids

        # Create new WooCommerce Categories from IML Categories
        if new_iml_category_ids:
            new_categories = []
            all_iml_categories = self.iml_get_category_list_request.run()
            new_iml_categories = [
                iml_category
                for iml_category in all_iml_categories
                if iml_category["category_id"] in new_iml_category_ids
            ]
            for new_iml_category in new_iml_categories:
                new_woocommerce_category = self.iml_category_transformer.transform(
                    new_iml_category
                )
                new_categories.append(new_woocommerce_category)
            response = self.woocommerce_batch_update_categories_request.run(
                new_categories
            )
            new_category_maps = []
            with self.category_id_table.batch_writer() as writer:
                for new_woocommerce_category in response.get("create", []):
                    category_map = {
                        "category_id": new_woocommerce_category["slug"],
                        "woocommerce_category_id": new_woocommerce_category["id"],
                    }
                    print("ATTEMPT: Writing category map to DynamoDB: ", category_map)
                    writer.put_item(Item=category_map)
                    print("SUCCESS: Wrote category map to DynamoDB: ", category_map)
                    new_category_maps.append(category_map)

        iml_item_ids = {product["short_code"] for product in products}

        # Get WooCommerce Categories for WooCommerce Product Create/Updates
        category_maps = new_category_maps + old_category_maps
        woocommerce_category_ids = [
            category_map["woocommerce_category_id"] for category_map in category_maps
        ]
        response = self.woocommerce_list_all_product_categories_request.run(
            ids=woocommerce_category_ids
        )
        woocommerce_categories_by_slug = {
            category["slug"]: category for category in response
        }

        # Identify Existing IML Products
        response = self.dynamodb.batch_get_item(
            RequestItems={
                "iml-item-id-table": {
                    "Keys": [{"item_id": str(item_id)} for item_id in iml_item_ids]
                }
            }
        )
        old_item_maps = [
            item for item in response.get("Responses", {}).get("item_id", [])
        ]
        old_iml_item_ids = {item["woocommerce_product_id"] for item in old_item_maps}
        new_iml_item_ids = iml_item_ids - old_iml_item_ids

        # Create new WooCommerce Products from IML Items
        if new_iml_item_ids:
            new_woocommerce_products = []
            new_iml_items = [
                iml_item
                for iml_item in products
                if iml_item["short_code"] in new_iml_item_ids
            ]
            for new_iml_item in new_iml_items:
                new_woocommerce_product = self.iml_item_transformer.transform(
                    {
                        **new_iml_item,
                        ImlItemTransformer.WOOCOMMERCE_CATEGORIES_BY_SLUG: woocommerce_categories_by_slug,
                    }
                )
                new_woocommerce_products.append(new_woocommerce_product)
            response = self.woocommerce_batch_update_products_request.run(
                new_woocommerce_products
            )
            new_item_maps = []
            with self.item_id_table.batch_writer() as writer:
                for new_woocommerce_product in response.get("create", []):
                    item_map = {
                        "item_id": new_woocommerce_product["slug"],
                        "woocommerce_product_id": new_woocommerce_product["id"],
                    }
                    print("ATTEMPT: Writing item map to DynamoDB: ", item_map)
                    writer.put_item(Item=item_map)
                    print("SUCCESS: Wrote item map to DynamoDB: ", item_map)
                    new_item_maps.append(item_map)

        # Update old WooCommerce Products from IML Items
        if old_iml_item_ids:
            pass
