from recor_product_transformer.libs.models.woocommerce.woocommerce_category import WooCommerceCategory
from recor_product_transformer.libs.models.woocommerce.woocommerce_dimensions import WooCommerceDimensions
from recor_product_transformer.libs.models.woocommerce.woocommerce_image import WooCommerceImage
from recor_product_transformer.libs.transformers.iml.iml_dimensions_transformer import (
    ImlDimensionsTransformer,
)
from recor_product_transformer.libs.transformers.transformer import Transformer
from recor_product_transformer.libs.models.woocommerce.woocommerce_product import (
    WooCommerceProduct,
)


class ImlItemTransformer(Transformer):
    WOOCOMMERCE_CATEGORIES_BY_SLUG = "WOOCOMMERCE_CATEGORIES_BY_SLUG"

    def __init__(self):
        self.iml_dimensions_transformer = ImlDimensionsTransformer()

    def transform(self, raw_json: dict):
        """
        :param raw_json: raw_json
        """
        return WooCommerceProduct(
            name=raw_json.get("item_desc"),
            sku=raw_json.get("item_id"),
            slug=raw_json.get("short_code"),
            images=self._get_images(raw_json),
            description=self._get_description(raw_json),
            stock_quantity=raw_json.get("qty_avail"),
            dimensions=self._get_dimensions(raw_json),
            categories=self._get_categories(raw_json),
            regular_price=raw_json.get("list_price")
        )

    def _get_categories(self, raw_json):
        woocommerce_categories = []
        woocommerce_category_map_by_slug = raw_json.get(self.WOOCOMMERCE_CATEGORIES_BY_SLUG)
        for iml_category_id in raw_json.get("category_id"):
            if iml_category_id in woocommerce_category_map_by_slug:
                woocommerce_category = woocommerce_category_map_by_slug[iml_category_id]
                woocommerce_categories.append(WooCommerceCategory(
                    id=woocommerce_category.get("id"),
                    name=woocommerce_category.get("name"),
                    slug=woocommerce_category.get("slug")
                ))
        return woocommerce_categories

    def _get_description(self, raw_json):
        extended_desc = raw_json.get("extended_desc")
        links = [link.get("name") + ": " + link.get("url") for link in raw_json.get("links", [])]
        description = ""
        if extended_desc:
            description += extended_desc
        if links:
            description += ", ".join(links)
        return description

    def _get_dimensions(self, raw_json):
        return WooCommerceDimensions(
            length=raw_json.get("length"),
            width=raw_json.get("width"),
            height=raw_json.get("height"),
        )

    def _get_images(self, raw_json):
        return [
            WooCommerceImage(
                src=raw_json.get("img_sml"),
                name="iml_img_sml"
            ),
            WooCommerceImage(
                src=raw_json.get("img_med"),
                name="iml_img_med"
            )
        ]
