from recor_layer.services.aws.dynamodb.dynamodb_service import DynamoDBService
from recor_layer.services.woocommerce.woocommerce_service import WooCommerceService


class ResetService:
    """
    Service that deletes all the categories and items from DynamoDB and WooCommerce. For development testing only.
    """

    def __init__(self, region_name: str = "us-east-1"):
        """
        Initializes the ResetService.
        """
        self.dynamodb_service = DynamoDBService(region_name)
        self.woocommerce_service = WooCommerceService()

    def run(self) -> None:
        """
        1. Retrieve and delete all items from iml-item-id-table
        2. Delete all products from Woocommerce
        3. Retrieve and delete all categories from iml-category-id-table
        4. Delete all categories from Woocommerce
        5. Set iml-counter.item_info_since to 0
        """
        # Retrieve and delete all items from iml-item-id-table
        items = self.dynamodb_service.get_all_dynamodb_items("iml-item-id-table")
        woocommerce_product_ids = [item.get("woocommerce_product_id") for item in items]
        print(
            f"ATTEMPT: Deleting ids from iml-item-id-table: {woocommerce_product_ids}"
        )
        self.dynamodb_service.delete_all_dynamodb_items("iml-item-id-table")
        print("SUCCESS: Successfully deleted ids from iml-item-id-table")

        # Delete all products from Woocommerce
        self.woocommerce_service.delete_products(woocommerce_product_ids)

        # Retrieve and delete all categories from iml-category-id-table
        categories = self.dynamodb_service.get_all_dynamodb_items(
            "iml-category-id-table"
        )
        woocommerce_category_ids = [
            category.get("woocommerce_category_id") for category in categories
        ]
        print(
            f"ATTEMPT: Deleting ids from iml-category-id-table: {woocommerce_category_ids}"
        )
        self.dynamodb_service.delete_all_dynamodb_items("iml-category-id-table")
        print("SUCCESS: Successfully deleted ids from iml-category-id-table")

        # Delete all categories from Woocommerce
        self.woocommerce_service.delete_categories(woocommerce_category_ids)

        # Update the counter in DynamoDB
        self.dynamodb_service.put_item(
            table_name=self.counter_table_name,
            item={
                "counter_name": "item_info_since",
                "counter": 0,
            },
        )

        print("SUCCESS: all categories and items from DynamoDB and WooCommerce deleted")
