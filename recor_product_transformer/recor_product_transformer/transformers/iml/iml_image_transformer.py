from recor_product_transformer.transformers.transformer import Transformer


class ImlImageTransformer(Transformer):
    def transform(self, raw_json: dict):
        """
        :param raw_json: raw_json
        """
        return raw_json
