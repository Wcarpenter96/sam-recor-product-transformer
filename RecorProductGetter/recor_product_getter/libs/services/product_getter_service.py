from recor_product_getter.libs.requests.woocommerce.woocommerce_get_counter_request import (
    WooCommerceGetCounterRequest,
)
from recor_product_getter.libs.services.iml.iml_item_publisher_service import (
    ImlItemPublisherService,
)


class ProductGetterService:
    def __init__(self):
        self.woocommerce_get_counter_request = WooCommerceGetCounterRequest()
        self.iml_item_publisher_service = ImlItemPublisherService()

    def run(self):
        counter = self.woocommerce_get_counter_request.run()
        self.iml_item_publisher_service.run(counter)
