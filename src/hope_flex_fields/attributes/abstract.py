from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Optional

from django import forms
from django.core.exceptions import ValidationError

if TYPE_CHECKING:
    from hope_flex_fields.models import FieldDefinition, FlexField

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
    validators = ()

    def __init__(self, context: "FieldDefinition"):
        self.owner = context

    @property
    def config(self):
        frm = self.config_class(self.owner.strategy_config, instance=self.owner)
        if frm.is_valid():
            return frm.cleaned_data
        raise ValidationError(frm.errors)

    @abstractmethod
    def get(self, instance: "Optional[FlexField]" = None) -> "Json": ...

    @abstractmethod
    def set(self, value: "Json"): ...
