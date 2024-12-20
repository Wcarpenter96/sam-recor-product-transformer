from typing import cast

import requests
from recor_category_transformer.libs.requests.iml.iml_base_request import ImlBaseRequest


class ImlGetCategoryListRequest(ImlBaseRequest):
    def run(self) -> dict:

        print("ATTEMPT: Getting Item Category List from IML")

        response = requests.get(
            self.base_url + "/item_category_list/", params=self.default_params
        )

        if response.ok:
            print("SUCCESS: Received Item Category List from IML")
            return cast(dict, response.json()["category_list"])
        else:
            raise Exception(response.text)
