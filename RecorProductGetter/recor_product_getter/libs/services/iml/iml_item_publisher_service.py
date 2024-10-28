import decimal
import os
from json import dumps

import boto3
import ijson
from recor_product_getter.libs.requests.iml.iml_get_item_info_request import (
    ImlGetItemInfoRequest,
)

"""
ijson works with file-like objects; that is, objects with a read method
wrap the response to make it look like a file that can be read
"""


class ResponseAsFileObject:
    def __init__(self, data):
        self.data = data

    def read(self, n):
        if n == 0:
            return b""
        return next(self.data, b"")


class ImlItemPublisherService:
    def __init__(self):
        self.iml_get_item_info_request = ImlGetItemInfoRequest()
        self.sqs_client = boto3.client("sqs")
        self.queue_url = os.getenv("SQS_QUEUE_URL")

    def run(self, counter, max_batch_items, max_total_items):
        response = ImlGetItemInfoRequest().run(counter)
        total_item_count = 0
        batch_item_count = 0
        batch_count = 0
        batch_items = []
        for item in ijson.items(
            ResponseAsFileObject(response.iter_content(chunk_size=65536)),
            "items.item",
            use_float=True,
        ):
            if total_item_count > max_total_items:
                print(
                    f"WARNING: {batch_count + 1} batches of {max_batch_items} Items is greater than the maximum total Items {max_total_items}."
                )
                break
            else:
                total_item_count += 1
                batch_item_count += 1
                batch_items.append(item)
                if batch_item_count == max_batch_items:
                    batch_count += 1
                    print(
                        f"ATTEMPT: Publishing Batch {batch_count} with {batch_item_count} Items to {self.queue_url}"
                    )
                    self.sqs_client.send_message(
                        QueueUrl=self.queue_url,
                        MessageBody=dumps(batch_items),
                    )
                    print(
                        f"SUCCESS: Published Batch {batch_count} with {batch_item_count} Items to {self.queue_url}"
                    )
                    batch_item_count = 0
                    batch_items = []
        print(
            f"SUCCESS: Published {batch_count * max_batch_items} Items to {self.queue_url}"
        )
