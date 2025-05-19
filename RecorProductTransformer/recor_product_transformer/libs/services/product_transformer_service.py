from typing import Dict, List, Set

from recor_layer.services.aws.dynamodb.dynamodb_service import DynamoDBService
from recor_layer.services.iml.iml_service import ImlService
from recor_layer.services.woocommerce.woocommerce_service import WooCommerceService
from recor_layer.transformers.iml.iml_item_transformer import ImlItemTransformer


class ProductTransformerService:
    """Orchestrates the transformation of IML products to WooCommerce."""

    def __init__(self, region_name: str = "us-east-1"):
        self.iml_item_transformer = ImlItemTransformer()
        self.dynamodb_service = DynamoDBService(region_name)
        self.woocommerce_service = WooCommerceService()
        self.iml_service = ImlService()

    def _fetch_existing_iml_category_map(
        self, iml_category_ids: Set[str]
    ) -> Dict[str, int]:
        """Fetches the mapping of IML category IDs to WooCommerce category IDs from DynamoDB."""
        keys = [{"category_id": category_id} for category_id in iml_category_ids]
        category_items = self.dynamodb_service.get_batch_items(
            "iml-category-id-table", keys
        )
        return {
            item["category_id"]: item.get("woocommerce_category_id")
            for item in category_items
        }

    def _fetch_existing_iml_product_map(self, iml_item_ids: Set[str]) -> Dict[str, int]:
        """Fetches the mapping of IML item IDs to WooCommerce product IDs from DynamoDB."""
        keys = [{"item_id": item_id} for item_id in iml_item_ids]
        item_items = self.dynamodb_service.get_batch_items("iml-item-id-table", keys)
        return {
            item["item_id"]: item.get("woocommerce_product_id") for item in item_items
        }

    def _transform_new_products(
        self, new_iml_items: List[Dict], old_category_id_map: Dict[str, int]
    ) -> List[Dict]:
        """Transforms new IML items into WooCommerce product format."""
        new_woocommerce_products = []
        for new_iml_item in new_iml_items:
            new_woocommerce_product = self.iml_item_transformer.transform(
                {
                    **new_iml_item,
                    ImlItemTransformer.CATEGORY_ID_MAP: old_category_id_map,
                }
            )
            new_woocommerce_products.append(new_woocommerce_product)
        return new_woocommerce_products

    def _transform_old_products(
        self,
        old_iml_items: List[Dict],
        old_category_id_map: Dict[str, int],
        old_item_id_map: Dict[str, int],
    ) -> List[Dict]:
        """Transforms existing IML items into WooCommerce product format for updates."""
        old_woocommerce_products = []
        for old_iml_item in old_iml_items:
            old_woocommerce_product = self.iml_item_transformer.transform(
                {
                    **old_iml_item,
                    ImlItemTransformer.CATEGORY_ID_MAP: old_category_id_map,
                    ImlItemTransformer.PRODUCT_ID_MAP: old_item_id_map,
                }
            )
            old_woocommerce_products.append(old_woocommerce_product)
        return old_woocommerce_products

    def _save_new_product_mappings(self, woocommerce_create_response: List[Dict]):
        """Saves the mapping of new WooCommerce product slugs to their IDs in DynamoDB."""
        new_item_maps = [
            {"item_id": product["slug"], "woocommerce_product_id": product["id"]}
            for product in woocommerce_create_response
            if "slug" in product and "id" in product
        ]
        if new_item_maps:
            self.dynamodb_service.put_batch_items("iml-item-id-table", new_item_maps)

    def run(self, products: List[Dict]):
        """Orchestrates the synchronization of IML products to WooCommerce."""
        iml_category_ids = {
            str(category_id)
            for product in products
            for category_id in product.get("category_id", [])
        }
        iml_item_ids = {str(product["short_code"]) for product in products}

        # Identify Existing IML Categories
        old_category_id_map = self._fetch_existing_iml_category_map(iml_category_ids)
        old_iml_category_ids = set(old_category_id_map.keys())
        new_iml_category_ids = iml_category_ids - old_iml_category_ids

        if new_iml_category_ids:
            warn_msg = f"WARN: New IML Categories: {new_iml_category_ids}. Run RecorCategoryTransformer to resolve"
            print(warn_msg)

        # Identify Existing IML Products
        old_item_id_map = self._fetch_existing_iml_product_map(iml_item_ids)
        old_iml_item_ids = set(old_item_id_map.keys())
        new_iml_item_ids = iml_item_ids - old_iml_item_ids

        # Build New WooCommerce Products
        new_woocommerce_products = []
        if new_iml_item_ids:
            new_iml_items = [
                iml_item
                for iml_item in products
                if str(iml_item.get("short_code")) in new_iml_item_ids
            ]
            new_woocommerce_products = self._transform_new_products(
                new_iml_items, old_category_id_map
            )

        # Build Old WooCommerce Products for Update
        old_woocommerce_products = []
        if old_iml_item_ids:
            old_iml_items = [
                iml_item
                for iml_item in products
                if str(iml_item.get("short_code")) in old_iml_item_ids
            ]
            old_woocommerce_products = self._transform_old_products(
                old_iml_items, old_category_id_map, old_item_id_map
            )

        # Batch Create New/Update Old WooCommerce Products
        woocommerce_response = self.woocommerce_service.batch_update_products(
            new_products=new_woocommerce_products, old_products=old_woocommerce_products
        )

        # Add new WooCommerce Product to Item Map
        self._save_new_product_mappings(woocommerce_response.get("create", []))
