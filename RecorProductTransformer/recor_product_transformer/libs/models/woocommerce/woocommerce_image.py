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
