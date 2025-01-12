from recor_product_getter.libs.services.iml.iml_item_publisher_service import (
    ImlItemPublisherService,
)
import boto3


class ProductGetterService:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        self.counter_table = boto3.resource("dynamodb").Table("iml-counter-table")
        self.iml_item_publisher_service = ImlItemPublisherService()

    def run(self, max_batch_items, max_total_items):

        response = self.dynamodb.get_item(
            TableName= "iml-counter-table",
            Key = {
                "counter_name": {
                    "S": "item_info_since"
                }
            }
        )

        current_update_seq = 0
        for record in response.get("Responses", {}).get("iml-counter-table", []):
            if record["counter_name"] == "item_info_since":
                current_update_seq = int(record["counter"])

        iml_update_seq = self.iml_item_publisher_service.run(current_update_seq, max_batch_items, max_total_items)

        with self.counter_table.batch_writer() as writer:
            writer.put_item({
                "counter_name": "item_info_since",
                "counter": iml_update_seq,
            })

        print(f"SUCCESS: Updated item_info_since={iml_update_seq} counter in iml-counter-table")
