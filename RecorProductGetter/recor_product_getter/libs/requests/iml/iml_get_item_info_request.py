import requests
from recor_product_getter.libs.requests.iml.iml_base_request import ImlBaseRequest

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


class ImlGetItemInfoRequest(ImlBaseRequest):

    def run(self, counter: int):

        print("ATTEMPT: Getting Item Info Response from IML")
        item_info = self.base_url + "/item_info_since/" + str(counter)

        response = requests.get(item_info, params=self.default_params, stream=True)

        if response.ok:
            print("SUCCESS: Received Item Info Response from IML")
            return response
        else:
            raise Exception(response.text)
