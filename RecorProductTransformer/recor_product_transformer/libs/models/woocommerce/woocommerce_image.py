from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WooCommerceImage:
    """
    Object that holds the attributes and data required for a Woocommerce image
    """

    id: Optional[int] = None
    src: Optional[str] = None
    name: Optional[str] = None

    def to_json(self) -> dict:
        """
        Transforms a WooCommerceImage instance into json
        Returns:
            Dict[str, Any]: The json transformation
        """
        return {
            "id": self.id,
            "src": self.src,
            "name": self.name,
        }
