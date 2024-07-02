import inspect
import logging
from typing import TYPE_CHECKING

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from django_regex.fields import RegexField
from django_regex.validators import RegexValidator
from strategy_field.fields import StrategyClassField

from .fields import FlexField
from .registry import field_registry

if TYPE_CHECKING:
    from .forms import FieldsetForm

logger = logging.getLogger(__name__)

DEFAULT_ATTRS = {
    "required": False,
    "label": None,
    "help_text": "",
}


def get_default_attrs():
    return DEFAULT_ATTRS


class TestForm(forms.Form):
    fieldset = None


class FieldDefinitionManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class FieldDefinition(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=500, blank=True, null=True, default="")
    field_type = StrategyClassField(registry=field_registry)
    attrs = models.JSONField(default=get_default_attrs, blank=True)
    regex = RegexField(blank=True, null=True, validators=[RegexValidator()])
    validation = models.TextField(blank=True, null=True)
    objects = FieldDefinitionManager()

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    def clean(self):
        try:
            self.set_default_arguments()
            self.get_field()
            self.name = slugify(str(self.name))
        except TypeError as e:
            raise ValidationError(e)

    def set_default_arguments(self):
        if self.attrs in [None, "null", ""]:
            self.attrs = DEFAULT_ATTRS
        elif isinstance(self.attrs, str):
            self.attrs = DEFAULT_ATTRS

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
            field_class = type(f"{self.name}Field", (FlexField, self.field_type), {})
            fld = field_class(**kwargs)
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise
        return fld


class FieldsetManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Fieldset(models.Model):
    name = models.CharField(max_length=255, unique=True)
    objects = FieldsetManager()

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    def get_form(self) -> "type[FieldsetForm]":
        fields: dict[str, forms.Field] = {}
        field: FieldsetField
        for field in self.fields.filter():
            fld = field.get_field()
            fields[field.name] = fld
        form_class_attrs = {
            "FieldsetForm": self,
            **fields,
        }
        return type(f"{self.name}FieldsetForm", (TestForm,), form_class_attrs)

    def validate(self, data):
        form_class = self.get_form()
        form: FieldsetForm = form_class(data=data)
        if form.is_valid():
            return True
        else:
            raise ValidationError(form.errors)


class FieldsetFieldManager(models.Manager):
    def get_by_natural_key(self, name, fieldset_name):
        return self.get(name=name, fieldset__name=fieldset_name)


class FieldsetField(models.Model):
    name = models.CharField(max_length=255, unique=True)
    fieldset = models.ForeignKey(
        Fieldset, on_delete=models.CASCADE, related_name="fields"
    )
    field = models.ForeignKey(
        FieldDefinition, on_delete=models.CASCADE, related_name="instances"
    )
    overrides = models.JSONField(default=dict, blank=True)
    objects = FieldsetFieldManager()

    class Meta:
        unique_together = [["fieldset", "name"]]

    def natural_key(self):
        return self.name, self.fieldset.name

    def get_field(self):
        return self.field.get_field()
