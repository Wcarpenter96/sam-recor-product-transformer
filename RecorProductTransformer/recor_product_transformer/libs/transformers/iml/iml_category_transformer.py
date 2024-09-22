from recor_product_transformer.libs.models.woocommerce.woocommerce_category import (
    WooCommerceCategory,
)
from recor_product_transformer.libs.models.woocommerce.woocommerce_image import (
    WooCommerceImage,
)
from recor_product_transformer.libs.transformers.transformer import Transformer


class ImlCategoryTransformer(Transformer):

    def transform(self, raw_json: dict):
        """
        :param raw_json: raw_json
        """
        return WooCommerceCategory(
            name=raw_json.get("title"),
            slug=raw_json.get("category_id"),
            image=self._get_image(raw_json),
        )

    def _get_image(self, raw_json):
        return WooCommerceImage(
            src=raw_json.get("img"),
        )
