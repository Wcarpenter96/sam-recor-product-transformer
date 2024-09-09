from recor_product_transformer.libs.transformers.iml.iml_category_transformer import (
    ImlCategoryTransformer,
)
from recor_product_transformer.libs.transformers.iml.iml_dimensions_transformer import (
    ImlDimensionsTransformer,
)
from recor_product_transformer.libs.transformers.iml.iml_image_transformer import (
    ImlImageTransformer,
)
from recor_product_transformer.libs.transformers.transformer import Transformer


class ImlItemTransformer(Transformer):

    def __init__(self):
        self.iml_category_transformer = ImlCategoryTransformer()
        self.iml_image_transformer = ImlImageTransformer()
        self.iml_dimensions_transformer = ImlDimensionsTransformer()

    def transform(self, raw_json: dict):
        """
        :param raw_json: raw_json
        """
        return raw_json
