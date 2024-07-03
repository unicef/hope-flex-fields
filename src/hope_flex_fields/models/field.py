import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from ..fields import FlexField
from ..utils import namefy
from ..validators import JsValidator, ReValidator
from .base import AbstractField
from .definition import FieldDefinition
from .fieldset import Fieldset

logger = logging.getLogger(__name__)


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
