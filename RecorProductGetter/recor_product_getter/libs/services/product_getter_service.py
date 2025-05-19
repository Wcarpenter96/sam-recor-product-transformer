from recor_layer.services.aws.dynamodb.dynamodb_service import DynamoDBService
from recor_product_getter.libs.services.iml.iml_item_publisher_service import (
    ImlItemPublisherService,
)


class ProductGetterService:
    """
    Service to get product information, update counters, and interact with IML.
    """

    def __init__(self, region_name: str = "us-east-1"):
        """
        Initializes the ProductGetterService.
        """
        self.dynamodb_service = DynamoDBService(region_name)
        self.iml_item_publisher_service = ImlItemPublisherService()
        self.counter_table_name = "iml-counter"  # Store table name as attribute

    def run(self, max_batch_items: int, max_total_items: int) -> None:
        """
        Runs the product getting process.

        Args:
            max_batch_items: Maximum number of items to retrieve in a single batch.
            max_total_items: Maximum number of total items to retrieve.
        """
        # Get current update sequence from DynamoDB
        response = self.dynamodb_service.get_batch_items(
            table_name=self.counter_table_name,
            keys=[{"counter_name": "item_info_since"}],
        )

        current_update_seq = 0
        for record in response:  # Simplified iteration
            if record.get("counter_name") == "item_info_since":
                current_update_seq = int(
                    record.get("counter", 0)
                )  # Default to 0 if counter is missing

        # Get updated item sequence from IML
        iml_update_seq = self.iml_item_publisher_service.run(
            current_update_seq, max_batch_items, max_total_items
        )

        # Update the counter in DynamoDB
        self.dynamodb_service.put_item(
            table_name=self.counter_table_name,
            item={
                "counter_name": "item_info_since",
                "counter": iml_update_seq,
            },
        )

        print(
            f"SUCCESS: Updated item_info_since={iml_update_seq} counter in {self.counter_table_name}"
        )
