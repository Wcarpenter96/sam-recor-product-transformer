import os
from json import dumps
from typing import Iterator, List

import ijson
from recor_layer.services.aws.sqs.sqs_service import SQSService
from recor_layer.services.iml.iml_service import ImlService
from recor_product_getter.libs.services.utils.file_response import FileResponse
from requests import Response


class ImlItemPublisherService:
    """
    Service to publish item information from IML to an SQS queue.
    """

    def __init__(self):
        """
        Initializes the ImlItemPublisherService.
        """
        self.iml_service = ImlService()
        self.queue_url = os.getenv("SQS_QUEUE_URL")
        if not self.queue_url:
            raise ValueError("SQS_QUEUE_URL environment variable must be set")
        self.sqs_service = SQSService(self.queue_url)  # Use SQSService

    def _get_item_info_response(self, counter: int) -> Response:
        """
        Retrieves item information from the IML system.

        Args:
            counter: The counter value to use in the request.

        Returns:
            The response object from the IML request.

        Raises:
            Exception: If the IML request fails.
        """
        try:
            response = self.iml_service.get_item_info(counter=counter)
            response.raise_for_status()
            return response
        except Exception as e:
            raise Exception(f"Error fetching item info from IML: {e}") from e

    def _extract_items_from_response(
        self, response: Response, max_total_items: int
    ) -> Iterator[dict]:
        """
        Extracts item data from the IML response.

        Args:
            response: The response object from the IML system.
            max_total_items: The maximum number of items to extract.

        Returns:
            An iterator yielding individual item dictionaries.
        """
        total_item_count = 0
        for item in ijson.items(
            FileResponse(response.iter_content(chunk_size=65536)),
            "items.item",
            use_float=True,
        ):
            if total_item_count >= max_total_items:
                print(
                    f"WARNING: Extracted {total_item_count} items, but maximum total is {max_total_items}."
                )
                break
            total_item_count += 1
            yield item

    def _send_batch_to_sqs(self, batch_items: List[dict], batch_count: int) -> None:
        """
        Sends a batch of items to the SQS queue using SQSService.

        Args:
            batch_items: The list of items to send in the batch.
            batch_count: The current batch number.
        """
        print(
            f"ATTEMPT: Publishing Batch {batch_count} with {len(batch_items)} Items to {self.queue_url}"
        )
        self.sqs_service.send_message(message_body=dumps(batch_items))
        print(
            f"SUCCESS: Published Batch {batch_count} with {len(batch_items)} Items to {self.queue_url}"
        )

    def _extract_last_update_seq(self, response: Response) -> int:
        """
        Extracts the last update sequence from the IML response.

        Args:
            response: The response object from the IML system.

        Returns:
            The last update sequence number.

        Raises:
            ValueError: If the last_update_seq is not found or is invalid.
        """
        print("ATTEMPT: Extracting last_update_seq from IML response")
        for last_update_seq in ijson.items(
            FileResponse(response.iter_content(chunk_size=65536)),
            "last_update_seq",
        ):
            try:
                last_update_seq_int = int(last_update_seq)
                print(f"Found last update seq={last_update_seq_int}")
                return last_update_seq_int
            except ValueError:
                raise ValueError(
                    f"Invalid last_update_seq value: {last_update_seq}"
                ) from None
        raise ValueError("last_update_seq not found in IML response")

    def run(self, counter: int, max_batch_items: int, max_total_items: int) -> int:
        """
        Runs the item publishing process.

        Args:
            counter: The starting counter value for retrieving items.
            max_batch_items: The maximum number of items to include in each SQS message.
            max_total_items: The maximum number of items to process in total.

        Returns:
            The last update sequence number from the IML response.
        """
        response = self._get_item_info_response(counter)

        batch_item_count = 0
        batch_count = 0
        batch_items = []

        for item in self._extract_items_from_response(response, max_total_items):
            batch_items.append(item)
            batch_item_count += 1

            if batch_item_count == max_batch_items:
                batch_count += 1
                self._send_batch_to_sqs(batch_items, batch_count)
                batch_items = []
                batch_item_count = 0

        # Send any remaining items in the last batch
        if batch_items:
            batch_count += 1
            self._send_batch_to_sqs(batch_items, batch_count)

        print(
            f"SUCCESS: Published {batch_count * max_batch_items} Items to {self.queue_url}"
        )

        last_update_seq = self._extract_last_update_seq(response)
        return last_update_seq
