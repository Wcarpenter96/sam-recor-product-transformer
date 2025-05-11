import boto3
from recor_layer.requests.iml.iml_get_category_list_request import (
    ImlGetCategoryListRequest,
)
from recor_layer.requests.woocommerce.woocommerce_batch_update_categories_request import (
    WooCommerceBatchUpdateCategoriesRequest,
)
from recor_layer.requests.woocommerce.woocommerce_list_all_categories_request import (
    WooCommerceListAllCategoriesRequest,
)
from recor_layer.transformers.iml.iml_category_transformer import (
    ImlCategoryTransformer,
)

MAX_CATEGORY_UPDATE_DEPTH = 10


def recursively_collect_parent_category_ids(
    new_iml_category, all_categories, parent_category_id_map
):
    category_id = str(new_iml_category.get("category_id"))
    parent_category_id = str(new_iml_category.get("parent_id", "-1"))
    parent_category_id_map[category_id] = parent_category_id
    if parent_category_id != "-1":
        parent_category = [
            iml_category
            for iml_category in all_categories
            if str(iml_category["category_id"]) == parent_category_id
        ][0]
        return recursively_collect_parent_category_ids(
            parent_category, all_categories, parent_category_id_map
        )


class CategoryTransformerService:
    def __init__(self):
        self.iml_get_category_list_request = ImlGetCategoryListRequest()
        self.woocommerce_batch_update_categories_request = (
            WooCommerceBatchUpdateCategoriesRequest()
        )
        self.woocommerce_list_all_product_categories_request = (
            WooCommerceListAllCategoriesRequest()
        )
        self.iml_category_transformer = ImlCategoryTransformer()
        self.dynamodb = boto3.resource("dynamodb")
        self.category_id_table = boto3.resource("dynamodb").Table(
            "iml-category-id-table"
        )

    def run(self, max_batch_categories, max_total_categories):
        all_categories = self.iml_get_category_list_request.run()
        if len(all_categories) > max_total_categories:
            print(
                f"Transforming ({max_total_categories}/{len(all_categories)}) categories"
            )
            remaining_categories = all_categories[:max_total_categories]
        else:
            remaining_categories = all_categories
        while len(remaining_categories) > 0:
            print(
                f"Transforming first {max_batch_categories} of remaining {len(remaining_categories)} categories"
            )
            categories = remaining_categories[:max_batch_categories]
            remaining_categories = remaining_categories[max_batch_categories:]
            self.transform_categories(categories, all_categories)
        print(f"SUCCESS: transformed categories")

    def transform_categories(self, categories, all_categories):
        # Collect parent category ids of categories
        parent_category_id_map = {}
        for category in categories:
            recursively_collect_parent_category_ids(
                category, all_categories, parent_category_id_map
            )

        # Identify Existing Categories
        response = self.dynamodb.batch_get_item(
            RequestItems={
                "iml-category-id-table": {
                    "Keys": [
                        {"category_id": str(category_id)}
                        for category_id in parent_category_id_map.keys()
                    ]
                }
            }
        )
        old_category_id_map = {}
        for category in response.get("Responses", {}).get("iml-category-id-table", []):
            old_category_id_map[category["category_id"]] = category[
                "woocommerce_category_id"
            ]

        new_iml_category_ids = (
            parent_category_id_map.keys() - old_category_id_map.keys()
        )

        category_id_map = old_category_id_map.copy()
        # Create categories that have no parent
        category_ids_no_parent = {
            category_id
            for category_id in new_iml_category_ids
            if parent_category_id_map[category_id] == "-1"
        }
        self.write_categories(category_ids_no_parent, all_categories, category_id_map)

        i = 0
        while (
            len(new_iml_category_ids - category_id_map.keys()) > 0
            and i < MAX_CATEGORY_UPDATE_DEPTH
        ):
            # Create categories whose parent exist in WooCommerce
            category_ids_existing_parent = {
                category_id
                for category_id in new_iml_category_ids
                if category_id not in category_id_map.keys()
                and parent_category_id_map[category_id] in category_id_map.keys()
            }
            self.write_categories(
                category_ids_existing_parent, all_categories, category_id_map
            )
            i += 1

    def write_categories(self, category_ids, all_categories, category_id_map):
        new_iml_categories = [
            iml_category
            for iml_category in all_categories
            if str(iml_category["category_id"]) in category_ids
        ]
        if new_iml_categories:
            new_categories = []
            for iml_category in new_iml_categories:
                new_category = self.iml_category_transformer.transform(
                    {
                        **iml_category,
                        ImlCategoryTransformer.CATEGORY_ID_MAP: category_id_map,
                    }
                )
                new_categories.append(new_category)
            print("ATTEMPT: Updating WooCommerce categories: ", new_categories)
            response = self.woocommerce_batch_update_categories_request.run(
                new_categories, []
            )
            print("SUCCESS: Batch updated categories, response: ", response)
            with self.category_id_table.batch_writer() as writer:
                for new_woocommerce_category in response.get("create", []):
                    if "error" in new_woocommerce_category:
                        print("ERROR: Unable to create WooCommerce category: ", new_woocommerce_category)
                        continue
                    woocommerce_category_id = new_woocommerce_category["id"]
                    iml_category_id = new_woocommerce_category["slug"]
                    category_map = {
                        "category_id": iml_category_id,
                        "woocommerce_category_id": woocommerce_category_id,
                    }
                    print("ATTEMPT: Writing category map to DynamoDB: ", category_map)
                    writer.put_item(Item=category_map)
                    print("SUCCESS: Wrote category map to DynamoDB: ", category_map)
                    category_id_map[iml_category_id] = woocommerce_category_id
