import inspect
import json
import logging

from django.db import models
from django.utils.translation import gettext as _

from strategy_field.fields import StrategyClassField

from ..fields import FlexField
from ..registry import field_registry
from ..utils import camelcase
from ..validators import JsValidator, ReValidator
from .base import DEFAULT_ATTRS, AbstractField

logger = logging.getLogger(__name__)


class FieldDefinitionManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class FieldDefinition(AbstractField):
    field_type = StrategyClassField(registry=field_registry)
    objects = FieldDefinitionManager()

    class Meta:
        verbose_name = _("Field Definition")
        verbose_name_plural = _("Field Definitions")

    def natural_key(self):
        return (self.name,)

    def clean(self):
        self.set_default_arguments()
        self.name = camelcase(str(self.name))
        try:
            self.get_field()
        except TypeError:
            self.attrs = {}
            self.set_default_arguments()

    def set_default_arguments(self):
        # defaults = {"label": namefy(self.name), **DEFAULT_ATTRS}
        if self.attrs in [None, "null", ""]:
            self.attrs = DEFAULT_ATTRS

        elif isinstance(self.attrs, str):
            try:
                self.attrs = json.loads(self.attrs)
            except json.JSONDecodeError:
                self.attrs = DEFAULT_ATTRS
        if not isinstance(self.attrs, dict) or not self.attrs:
            self.attrs = DEFAULT_ATTRS
        if self.field_type:
            sig: inspect.Signature = inspect.signature(self.field_type)
            merged = {
                k.name: k.default
                for __, k in sig.parameters.items()
                if k.default not in [inspect.Signature.empty]
            }
            merged.update(**self.attrs)
            self.attrs = merged

    @property
    def required(self):
        return self.attrs.get("required", False)

    def get_field(self) -> "FlexField":
        try:
            kwargs = dict(self.attrs)
            validators = []
            if self.validation:
                validators.append(JsValidator(self.validation))
            if self.regex:
                validators.append(ReValidator(self.regex))

            kwargs["validators"] = validators
            field_class = type(f"{self.name}Field", (FlexField, self.field_type), {})
            fld = field_class(**kwargs)
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise
        return fld
