from recor_category_transformer.libs.models.woocommerce.woocommerce_category import (
    WooCommerceCategory,
)
from recor_category_transformer.libs.models.woocommerce.woocommerce_image import (
    WooCommerceImage,
)
from recor_category_transformer.libs.transformers.transformer import Transformer


class ImlCategoryTransformer(Transformer):
    CATEGORY_ID_MAP = "CATEGORY_ID_MAP"

    def transform(self, raw_json: dict):
        """
        :param raw_json: raw_json
        """
        return WooCommerceCategory(
            name=raw_json.get("title"),
            slug=str(raw_json.get("category_id")),
            image=self._get_image(raw_json),
            parent=raw_json.get(self.CATEGORY_ID_MAP, {}).get(
                str(raw_json.get("parent_id"))
            ),
        )

    def _get_image(self, raw_json):
        return WooCommerceImage(
            src=raw_json.get("img"),
            name=raw_json.get("title"),
        )
