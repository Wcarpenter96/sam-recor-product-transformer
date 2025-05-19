from typing import Dict, List, Set

from recor_layer.services.aws.dynamodb.dynamodb_service import DynamoDBService
from recor_layer.services.iml.iml_service import ImlService
from recor_layer.services.woocommerce.woocommerce_service import WooCommerceService
from recor_layer.transformers.iml.iml_category_transformer import ImlCategoryTransformer

MAX_CATEGORY_UPDATE_DEPTH = 10


def recursively_collect_parent_category_ids(
    new_iml_category: Dict,
    all_categories: List[Dict],
    parent_category_id_map: Dict[str, str],
) -> None:
    """Recursively collects parent category IDs from a nested list of IML categories."""
    category_id = str(new_iml_category.get("category_id"))
    parent_category_id = str(new_iml_category.get("parent_id", "-1"))
    parent_category_id_map[category_id] = parent_category_id
    if parent_category_id != "-1":
        parent_category = next(
            (
                iml_category
                for iml_category in all_categories
                if str(iml_category["category_id"]) == parent_category_id
            ),
            None,
        )
        if parent_category:
            recursively_collect_parent_category_ids(
                parent_category, all_categories, parent_category_id_map
            )


class CategoryTransformerService:
    """Transforms IML categories into WooCommerce categories and manages the synchronization."""

    def __init__(self, region_name: str = "us-east-1"):
        """Initializes the CategoryTransformerService with necessary services."""
        self.iml_category_transformer = ImlCategoryTransformer()
        self.woocommerce_service = WooCommerceService()
        self.iml_service = ImlService()
        self.dynamodb_service = DynamoDBService(region_name)

    def _fetch_existing_category_map(self, category_ids: Set[str]) -> Dict[str, int]:
        """Fetches the mapping of IML category IDs to WooCommerce category IDs from DynamoDB."""
        keys = [{"category_id": category_id} for category_id in category_ids]
        category_items = self.dynamodb_service.get_batch_items(
            "iml-category-id-table", keys
        )
        return {
            item["category_id"]: item.get("woocommerce_category_id")
            for item in category_items
        }

    def _transform_iml_categories(
        self, iml_categories: List[Dict], category_id_map: Dict[str, int]
    ) -> List[Dict]:
        """Transforms a list of IML categories into WooCommerce category format."""
        return [
            self.iml_category_transformer.transform(
                {
                    **iml_category,
                    ImlCategoryTransformer.CATEGORY_ID_MAP: category_id_map,
                }
            )
            for iml_category in iml_categories
        ]

    def _write_categories_to_woocommerce(
        self, new_categories: List[Dict]
    ) -> List[Dict]:
        """Creates new categories in WooCommerce."""
        print("ATTEMPT: Updating WooCommerce categories: ", new_categories)
        response = self.woocommerce_service.batch_update_categories(
            new_categories=new_categories, old_categories=[]
        )  # We are only creating, not updating
        print("SUCCESS: Batch updated categories, response: ", response)
        return response.get("create", [])

    def _save_category_mappings(
        self, woocommerce_create_response: List[Dict]
    ) -> Dict[str, int]:
        """Saves the mapping of IML category IDs to WooCommerce category IDs in DynamoDB."""
        new_category_id_map = {}
        items_to_write = []
        for new_woocommerce_category in woocommerce_create_response:
            if "error" in new_woocommerce_category:
                print(
                    "ERROR: Unable to create WooCommerce category: ",
                    new_woocommerce_category,
                )
                continue  # Important: Handle errors in individual category creation
            woocommerce_category_id = new_woocommerce_category["id"]
            iml_category_id = new_woocommerce_category["slug"]  # Corrected
            new_category_id_map[iml_category_id] = woocommerce_category_id
            category_map = {
                "category_id": iml_category_id,
                "woocommerce_category_id": woocommerce_category_id,
            }
            items_to_write.append(category_map)

        if items_to_write:
            self.dynamodb_service.put_batch_items(
                "iml-category-id-table", items_to_write
            )
        return new_category_id_map

    def run(self, max_batch_categories: int, max_total_categories: int):
        """
        Orchestrates the process of transforming and synchronizing IML categories to WooCommerce.

        Args:
            max_batch_categories: The maximum number of categories to process in each batch.
            max_total_categories: The maximum number of categories to process in total.
        """
        all_categories = self.iml_service.get_category_list()  # Use ImlService
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
            self.transform_and_write_categories(categories, all_categories)
        print("SUCCESS: transformed categories")

    def transform_and_write_categories(
        self, categories: List[Dict], all_categories: List[Dict]
    ) -> None:
        """
        Transforms and writes categories to WooCommerce, handling parent-child relationships.

        This method now contains the core logic for transforming categories and writing
        them to WooCommerce, including handling the parent category relationships.
        """
        # Collect parent category ids of categories
        parent_category_id_map = {}
        for category in categories:
            recursively_collect_parent_category_ids(
                category, all_categories, parent_category_id_map
            )

        # Identify Existing Categories
        old_category_id_map = self._fetch_existing_category_map(
            set(parent_category_id_map.keys())
        )

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
            # Create categories whose parents exist in WooCommerce
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

    def write_categories(
        self,
        category_ids: Set[str],
        all_categories: List[Dict],
        category_id_map: Dict[str, int],
    ) -> None:
        """Writes categories to WooCommerce and saves the mappings."""
        new_iml_categories = [
            iml_category
            for iml_category in all_categories
            if str(iml_category["category_id"]) in category_ids
        ]
        if new_iml_categories:
            new_categories = self._transform_iml_categories(
                new_iml_categories, category_id_map
            )
            woocommerce_response = self._write_categories_to_woocommerce(new_categories)
            new_category_mappings = self._save_category_mappings(woocommerce_response)
            category_id_map.update(new_category_mappings)
