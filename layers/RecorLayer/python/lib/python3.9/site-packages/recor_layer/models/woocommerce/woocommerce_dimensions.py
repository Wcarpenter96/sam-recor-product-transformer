from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WooCommerceDimensions:
    """
    Object that holds the attributes and data required for Woocommerce product dimensions
    """

    length: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None

    def to_json(self) -> dict:
        """
        Transforms a WooCommerceDimensions instance into json
        Returns:
            Dict[str, Any]: The json transformation
        """
        return {
            "length": self.length,
            "width": self.width,
            "height": self.height,
        }
