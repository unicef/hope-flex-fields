import inspect
import json
import logging
from typing import TYPE_CHECKING

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from django_regex.fields import RegexField
from django_regex.validators import RegexValidator
from strategy_field.fields import StrategyClassField

from .fields import FlexField
from .registry import field_registry
from .utils import camelcase, namefy
from .validators import JsValidator, ReValidator

if TYPE_CHECKING:
    from .forms import FieldsetForm

logger = logging.getLogger(__name__)

DEFAULT_ATTRS = {
    "required": False,
    # "label": None,
    "help_text": "",
}


def get_default_attrs():
    return dict(**DEFAULT_ATTRS)


class TestForm(forms.Form):
    fieldset = None


class AbstractField(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=500, blank=True, null=True, default="")
    attrs = models.JSONField(default=dict, blank=True)
    regex = RegexField(blank=True, null=True, validators=[RegexValidator()])
    validation = models.TextField(blank=True, null=True, default="")

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


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


class FieldsetManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Fieldset(models.Model):
    name = models.CharField(max_length=255, unique=True)
    objects = FieldsetManager()

    class Meta:
        verbose_name = _("Fieldset")
        verbose_name_plural = _("Fieldsets")

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
        form_class_attrs = {"FieldsetForm": self, **fields}
        return type(f"{self.name}FieldsetForm", (TestForm,), form_class_attrs)

    def validate(self, data):
        form_class = self.get_form()
        form: FieldsetForm = form_class(data=data)
        if form.is_valid():
            return True
        else:
            self.errors = form.errors
            raise ValidationError(form.errors)


class FieldsetFieldManager(models.Manager):
    def get_by_natural_key(self, name, fieldset_name):
        return self.get(name=name, fieldset__name=fieldset_name)


class FieldsetField(AbstractField):
    fieldset = models.ForeignKey(
        Fieldset, on_delete=models.CASCADE, related_name="fields"
    )
    field = models.ForeignKey(
        FieldDefinition, on_delete=models.CASCADE, related_name="instances"
    )

    objects = FieldsetFieldManager()

    class Meta:
        unique_together = [["fieldset", "name"]]
        verbose_name = _("Fieldset Field")
        verbose_name_plural = _("Fieldset Fields")

    def validate_attrs(self, attrs):
        attrs = self.get_merged_attrs()
        try:
            self.get_field(attrs)
        except Exception as e:
            raise ValidationError(e)

    def clean(self):
        self.name = namefy(str(self.name))
        self.validate_attrs(self.attrs)

    def natural_key(self):
        return self.name, self.fieldset.name

    def get_merged_attrs(self):
        attrs = dict(**self.field.attrs)
        if isinstance(self.attrs, dict):
            attrs.update(self.attrs)
        return attrs

    def get_field(self, kwargs=None) -> "FlexField":
        try:
            if not kwargs:
                kwargs = self.get_merged_attrs()
            validators = []
            if self.validation:
                validators.append(JsValidator(self.validation))
            elif self.field.validation:
                validators.append(JsValidator(self.field.validation))

            if self.regex:
                validators.append(ReValidator(self.regex))
            elif self.field.regex:
                validators.append(ReValidator(self.field.regex))

            kwargs["validators"] = validators
            field_class = type(
                f"{self.name}Field", (FlexField, self.field.field_type), {}
            )
            fld = field_class(**kwargs)
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise
        return fld
