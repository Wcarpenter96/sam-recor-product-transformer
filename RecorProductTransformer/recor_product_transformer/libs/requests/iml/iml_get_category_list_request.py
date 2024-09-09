from typing import cast

import requests
from recor_product_transformer.libs.requests.iml.iml_base_request import ImlBaseRequest


class ImlGetCategoryListRequest(ImlBaseRequest):
    def run(self) -> dict:
        response = requests.get(
            self.base_url + "/item_category_list/", params=self.default_params
        )
        if response.ok:
            return cast(dict, response.json())
        else:
            raise Exception(response.text)
