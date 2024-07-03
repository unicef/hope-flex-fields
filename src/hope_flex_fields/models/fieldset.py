from typing import TYPE_CHECKING

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from .base import TestForm

if TYPE_CHECKING:
    from ..forms import FieldDefinitionForm
    from .field import FieldsetField


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

    def get_form(self) -> "type[FieldDefinitionForm]":
        fields: dict[str, forms.Field] = {}
        field: "FieldsetField"
        for field in self.fields.filter():
            fld = field.get_field()
            fields[field.name] = fld
        form_class_attrs = {"FieldsetForm": self, **fields}
        return type(f"{self.name}FieldsetForm", (TestForm,), form_class_attrs)

    def validate(self, data):
        form_class = self.get_form()
        form: "FieldDefinitionForm" = form_class(data=data)
        if form.is_valid():
            return True
        else:
            self.errors = form.errors
            raise ValidationError(form.errors)
