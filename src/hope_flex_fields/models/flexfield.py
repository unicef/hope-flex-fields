import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext as _

from ..fields import FlexFormMixin
from ..utils import namefy
from ..validators import JsValidator, ReValidator
from .base import AbstractField
from .definition import FieldDefinition
from .fieldset import Fieldset

logger = logging.getLogger(__name__)


class FieldsetFieldManager(models.Manager):
    def get_by_natural_key(self, name, fieldset_name):
        return self.get(name=name, fieldset__name=fieldset_name)


class FlexField(AbstractField):
    fieldset = models.ForeignKey(
        Fieldset, on_delete=models.CASCADE, related_name="fields"
    )
    field = models.ForeignKey(
        FieldDefinition, on_delete=models.CASCADE, related_name="instances"
    )

    objects = FieldsetFieldManager()

    class Meta:
        verbose_name = _("Flex Field")
        verbose_name_plural = _("flex Fields")
        constraints = (
            UniqueConstraint(fields=("name", "fieldset"), name="flexfield_unique_name"),
            UniqueConstraint(fields=("slug", "fieldset"), name="flexfield_unique_slug"),
        )

    def __str__(self):
        return self.name

    def base_type(self):
        return self.field.field_type.__name__

    def validate_attrs(self):
        try:
            self.get_field()
        except Exception as e:
            raise ValidationError(e)

    def clean(self):
        self.name = namefy(str(self.name))
        self.validate_attrs()

    def natural_key(self):
        return self.name, self.fieldset.name

    def get_merged_attrs(self):
        attrs = dict(**self.field.attrs)
        if isinstance(self.attrs, dict):
            attrs.update(self.attrs)
        return attrs

    def get_field(self, override_attrs=None, **extra) -> "FlexFormMixin":
        try:
            if override_attrs is not None:
                kwargs = dict(override_attrs)
            else:
                kwargs = self.get_merged_attrs()
                kwargs.update(extra)
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
                f"{self.name}Field",
                (FlexFormMixin, self.field.field_type),
                {"flex_field": self},
            )
            fld = field_class(**kwargs)
        except Exception as e:  # pragma: no cover
            logger.exception(e)
            raise TypeError(f"Error creating field for FlexField {self.name}: {e}")
        return fld
