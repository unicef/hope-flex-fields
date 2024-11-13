import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext as _

from ..exceptions import FlexFieldCreationError
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
    fieldset = models.ForeignKey(Fieldset, on_delete=models.CASCADE, related_name="fields")
    definition = models.ForeignKey(FieldDefinition, on_delete=models.CASCADE, related_name="instances")
    master = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE, related_name="+")

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

    @property
    def attributes(self):
        return self.attrs

    @attributes.setter
    def attributes(self, value):
        self.attrs = value

    @property
    def dependants(self):
        return FlexField.objects.filter(master=self)

    def base_type(self):
        return self.definition.field_type.__name__

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
        attrs = dict(**self.definition.get_attributes(self))
        if isinstance(self.attributes, dict):
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
            elif self.definition.validation:
                validators.append(JsValidator(self.definition.validation))

            if self.regex:
                validators.append(ReValidator(self.regex))
            elif self.definition.regex:
                validators.append(ReValidator(self.definition.regex))

            kwargs["validators"] = validators
            field_class = type(
                f"{self.name}Field",
                (FlexFormMixin, self.definition.field_type),
                {"flex_field": self},
            )
            fld = field_class(**kwargs)
            if self.definition.attributes_strategy.validators:
                fld.validators.extend([v(fld) for v in self.definition.attributes_strategy.validators])
        except Exception as e:  # pragma: no cover
            raise FlexFieldCreationError(f"Error creating field for FlexField {self.name}: {e}")
        return fld
