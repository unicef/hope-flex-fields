from typing import TYPE_CHECKING, Optional

from .abstract import AbstractAttributeHandler

if TYPE_CHECKING:
    from ..models import FlexField
    from ..types import Json


class DefaultAttributeHandler(AbstractAttributeHandler):
    def get(self, instance: "Optional[FlexField]" = None) -> "Json":
        return self.owner.attrs

    def set(self, value: "Json"):
        self.owner.attrs = value
