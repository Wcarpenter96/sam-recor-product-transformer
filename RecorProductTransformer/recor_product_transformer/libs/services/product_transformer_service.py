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


def recursively_collect_parent_category_ids(
    new_iml_category, all_iml_categories, parent_category_ids
):
    parent_category_ids.add(new_iml_category.get("category_id"))
    parent_category_id = new_iml_category.get("parent_id", -1)
    if parent_category_id != -1:
        parent_category = [
            iml_category
            for iml_category in all_iml_categories
            if iml_category["category_id"] == parent_category_id
        ][0]
        return recursively_collect_parent_category_ids(
            parent_category, all_iml_categories, parent_category_ids
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
            str(category_id)
            for product in products
            for category_id in product["category_id"]
        }

        # Identify Existing IML Categories
        response = self.dynamodb.batch_get_item(
            RequestItems={
                "iml-category-id-table": {
                    "Keys": [
                        {"category_id": category_id} for category_id in iml_category_ids
                    ]
                }
            }
        )
        old_category_id_map = {}
        for category in response.get("Responses", {}).get("iml-category-id-table", []):
            old_category_id_map[category["category_id"]] = category[
                "woocommerce_category_id"
            ]

        old_iml_category_ids = old_category_id_map.keys()
        new_iml_category_ids = iml_category_ids - old_iml_category_ids

        if new_iml_category_ids:
            warn_msg = f"WARN: New IML Categories: {new_iml_category_ids}. Run RecorCategoryTransformer to resolve"
            print(warn_msg)

        iml_item_ids = {str(product["short_code"]) for product in products}

        # Identify Existing IML Products
        response = self.dynamodb.batch_get_item(
            RequestItems={
                "iml-item-id-table": {
                    "Keys": [{"item_id": str(item_id)} for item_id in iml_item_ids]
                }
            }
        )
        old_item_id_map = {}
        for item in response.get("Responses", {}).get("iml-item-id-table", []):
            old_item_id_map[item["item_id"]] = item["woocommerce_product_id"]

        old_iml_item_ids = old_item_id_map.keys()
        new_iml_item_ids = iml_item_ids - old_iml_item_ids

        # Build New WooCommerce Products from IML Items
        new_woocommerce_products = []
        if new_iml_item_ids:
            new_iml_items = [
                iml_item
                for iml_item in products
                if iml_item["short_code"] in new_iml_item_ids
            ]
            for new_iml_item in new_iml_items:
                new_woocommerce_product = self.iml_item_transformer.transform(
                    {
                        **new_iml_item,
                        ImlItemTransformer.CATEGORY_ID_MAP: old_category_id_map,
                    }
                )
                new_woocommerce_products.append(new_woocommerce_product)

        # Build Old WooCommerce Products from IML Items
        old_woocommerce_products = []
        if old_iml_item_ids:
            old_iml_items = [
                iml_item
                for iml_item in products
                if str(iml_item["short_code"]) in old_iml_item_ids
            ]
            for old_iml_item in old_iml_items:
                old_woocommerce_product = self.iml_item_transformer.transform(
                    {
                        **old_iml_item,
                        ImlItemTransformer.CATEGORY_ID_MAP: old_category_id_map,
                        ImlItemTransformer.PRODUCT_ID_MAP: old_item_id_map,
                    }
                )
                old_woocommerce_products.append(old_woocommerce_product)

        # Batch Create New/Update Old WooCommerce Products
        response = self.woocommerce_batch_update_products_request.run(
            new_products=new_woocommerce_products, old_products=old_woocommerce_products
        )

        # Add new WooCommerce Product to Item Map
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
