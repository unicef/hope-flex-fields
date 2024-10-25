from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from django import forms

if TYPE_CHECKING:
    from hope_flex_fields.models import FieldDefinition

    from ..types import Json


class AttributeHandlerConfig(forms.Form):
    def __init__(self, *args, **kwargs):
        self.instance: FieldDefinition = kwargs.pop("instance")
        super().__init__(*args, **kwargs)

    def save(self):
        self.instance.strategy_config = self.cleaned_data
        self.instance.save(update_fields=["strategy_config"])


class AbstractAttributeHandler(metaclass=ABCMeta):
    dynamic = False
    config_class = AttributeHandlerConfig

    def __init__(self, context: "FieldDefinition"):
        self.owner = context

    @abstractmethod
    def get(self) -> "Json": ...

    @abstractmethod
    def set(self, value: "Json"): ...
