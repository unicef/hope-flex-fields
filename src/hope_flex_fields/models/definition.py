import logging
from inspect import isclass
from typing import TYPE_CHECKING

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext as _

from strategy_field.fields import StrategyClassField, StrategyField
from strategy_field.utils import fqn

from hope_flex_fields.utils import get_kwargs_from_field_class

from ..attributes.default import DefaultAttributeHandler
from ..attributes.registry import attributes_registry
from ..fields import FlexFormMixin
from ..registry import field_registry
from ..utils import get_common_attrs
from ..validators import JsValidator, ReValidator
from .base import AbstractField, BaseManager

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from .flexfield import FlexField


class FieldDefinitionManager(BaseManager):

    def get_by_natural_key(self, name):
        return self.get(name=name)

    def get_from_django_field(self, django_field: "forms.Field|type[forms.Field]"):
        if isinstance(django_field, forms.Field):
            fld = type(django_field)
        elif isclass(django_field) and issubclass(django_field, forms.Field):
            fld = django_field
        else:
            raise ValueError(django_field)
        name = fld.__name__
        return FieldDefinition.objects.get_or_create(
            name=name,
            field_type=fqn(fld),
            defaults={"attrs": get_kwargs_from_field_class(fld, get_common_attrs())},
        )[0]


class FieldDefinition(AbstractField):
    """This class is the equivalent django.forms.Field class, used to create reusable field types"""

    field_type = StrategyClassField(registry=field_registry, null=False, blank=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    system_data = models.JSONField(default=dict, blank=True, editable=False, null=True)
    attributes_strategy = StrategyField(
        registry=attributes_registry,
        default=fqn(DefaultAttributeHandler),
        help_text="Strategy to use for attributes retrieval",
    )
    strategy_config = models.JSONField(default=dict, blank=True, editable=False, null=True)
    validated = models.BooleanField(default=False, blank=True)

    objects = FieldDefinitionManager()

    class Meta:
        verbose_name = _("Field Definition")
        verbose_name_plural = _("Field Definitions")
        constraints = (
            UniqueConstraint(fields=("name",), name="fielddefinition_unique_name"),
            UniqueConstraint(fields=("slug",), name="fielddefinition_unique_slug"),
        )

    def __str__(self):
        return self.name

    @property
    def attributes(self):
        base = self.attrs
        try:
            return base | self.attributes_strategy.get()
        except Exception:
            self.validated = False
        return base

    @attributes.setter
    def attributes(self, value):
        self.attributes_strategy.set(value)

    def get_attributes(self, instance: "FlexField"):
        return self.attributes_strategy.get(instance)

    def natural_key(self):
        return (self.name,)

    def clean(self):
        self.name = str(self.name)
        try:
            self.get_field()
        except TypeError:
            raise ValidationError("Field definition cannot be validated")

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.attrs = self.get_default_attributes() | self.attrs
        if not update_fields:
            self.validated = False
        elif "validated" in update_fields:
            pass
        super().save(
            *args,
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def get_default_attributes(self):
        attrs = get_common_attrs()
        if self.field_type:
            return attrs | get_kwargs_from_field_class(self.field_type)
        return attrs

    def set_default_attributes(self):
        if self.field_type:
            attrs = self.get_default_attributes()
            self.attributes = attrs
        elif not isinstance(self.attrs, dict) or not self.attrs:
            self.attributes = get_common_attrs()

    @property
    def required(self):
        return self.attributes.get("required", False)

    def get_field(self, override_attrs=None):
        try:
            if override_attrs is not None:
                kwargs = dict(override_attrs)
            else:
                kwargs = dict(self.attributes)
            validators = []
            if self.validation:
                validators.append(JsValidator(self.validation))
            if self.regex:
                validators.append(ReValidator(self.regex))

            kwargs["validators"] = validators
            field_class = type(f"{self.name}Field", (FlexFormMixin, self.field_type), {})
            fld = field_class(**kwargs)
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise TypeError(f"Error creating field for FieldDefinition {self.name}: {e}")
        return fld
