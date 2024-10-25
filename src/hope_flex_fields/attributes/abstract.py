from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hope_flex_fields.models import FieldDefinition

    from ..types import Json


class AbstractAttributeHandler(metaclass=ABCMeta):
    dynamic = False

    def __init__(self, context: "FieldDefinition"):
        self.owner = context

    @abstractmethod
    def get(self) -> "Json": ...

    @abstractmethod
    def set(self, value: "Json"): ...
