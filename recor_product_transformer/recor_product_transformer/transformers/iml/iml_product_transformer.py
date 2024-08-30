from recor_product_transformer.transformers.transformer import Transformer
from recor_product_transformer.transformers import ImlCategoryTransformer
from recor_product_transformer.transformers.iml.iml_image_transformer import ImlImageTransformer
from recor_product_transformer.transformers.iml.iml_dimensions_transformer import ImlDimensionsTransformer

class ImlProductTransformer(Transformer):

    def __init__(self):
        self.iml_category_transformer = ImlCategoryTransformer()
        self.iml_image_transformer = ImlImageTransformer()
        self.iml_dimensions_transformer = ImlDimensionsTransformer()

    def transform(self, raw_json: dict):
        """
        :param raw_json: raw_json
        """
        return raw_json
