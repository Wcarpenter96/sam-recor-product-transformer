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

    def run(self, counter):
        response = ImlGetItemInfoRequest().run(counter)
        max_items = int(os.getenv("IML_MAX_ITEMS"))
        item_count = 0
        print(f"ATTEMPT: Publishing Item {item_count} to {self.queue_url}")
        for item in ijson.items(
            ResponseAsFileObject(response.iter_content(chunk_size=65536)),
            "items.item",
            use_float=True,
        ):
            if item_count >= max_items:
                return
            else:
                print(f"ATTEMPT: Publishing Item {item_count} to {self.queue_url}")
                self.sqs_client.send_message(
                    QueueUrl=self.queue_url,
                    MessageBody=dumps(item),
                )
                item_count += 1
                print(f"SUCCESS: Published Item {item_count} to {self.queue_url}")
        print(f"SUCCESS: Published {item_count} items to {self.queue_url}")
