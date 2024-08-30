from woocommerce import API
import os


class WooCommerceBaseRequest:
    def __init__(self):
        self.client = API(
            url=os.getenv('WOOCOMMERCE_BASE_URL'),
            consumer_key=os.getenv('WOOCOMMERCE_CONSUMER_KEY'),
            consumer_secret=os.getenv('WOOCOMMERCE_CONSUMER_SECRET'),
            version="wc/v3"
        )
