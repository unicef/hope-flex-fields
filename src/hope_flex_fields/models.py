import inspect
import logging
from typing import cast

from django import forms
from django.core.exceptions import ValidationError
from django.db import models

from django_regex.fields import RegexField
from django_regex.validators import RegexValidator
from strategy_field.fields import StrategyClassField

from .forms import FieldsetForm
from .registry import field_registry

logger = logging.getLogger(__name__)

DEFAULT_ATTRS = {
    "required": False,
    "label": None,
    "help_text": "",
}


class FieldDefinition(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=500, blank=True, null=True, default="")
    field_type = StrategyClassField(registry=field_registry)
    attrs = models.JSONField(default=DEFAULT_ATTRS, blank=True)
    regex = RegexField(blank=True, null=True, validators=[RegexValidator()])
    validation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def clean(self):
        try:
            self.set_default_arguments()
            self.get_field()
        except TypeError as e:
            raise ValidationError(e)

    def set_default_arguments(self):
        stored = self.attrs or {}
        sig: inspect.Signature = inspect.signature(self.field_type)
        defaults = {
            k.name: k.default
            for __, k in sig.parameters.items()
            if k.default not in [inspect.Signature.empty]
        }
        defaults.update(**stored)
        self.attrs = defaults

    @property
    def required(self):
        return self.attrs.get("required", False)

    def get_field(self) -> forms.Field:
        try:
            kwargs = dict(self.attrs)
            fld = cast(forms.Field, self.field_type(**kwargs))  # noqa
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise
        return fld


class Fieldset(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_form(self) -> type[FieldsetForm]:
        fields: dict[str, forms.Field] = {}
        field: FieldsetField
        for field in self.fields.filter():
            fld = field.get_field()
            fields[field.label] = fld
        form_class_attrs = {
            "FieldsetForm": self,
            **fields,
        }
        return type(f"{self.name}FieldsetForm", (FieldsetForm,), form_class_attrs)

    def validate(self, data):
        form_class = self.get_form()
        form: FieldsetForm = form_class(data=data)
        if form.is_valid():
            return True
        else:
            raise ValidationError(form.errors)


class FieldsetField(models.Model):
    label = models.CharField(max_length=255)
    fieldset = models.ForeignKey(
        Fieldset, on_delete=models.CASCADE, related_name="fields"
    )
    field = models.ForeignKey(
        FieldDefinition, on_delete=models.CASCADE, related_name="instances"
    )
    overrides = models.JSONField(default=dict, blank=True)

    def get_field(self):
        return self.field.get_field()
