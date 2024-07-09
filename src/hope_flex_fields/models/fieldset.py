from typing import TYPE_CHECKING

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from .base import FlexForm, ValidatorMixin

if TYPE_CHECKING:
    from ..forms import FieldDefinitionForm
    from .flexfield import FlexField


class FieldsetManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Fieldset(ValidatorMixin, models.Model):
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    extends = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    objects = FieldsetManager()

    class Meta:
        verbose_name = _("Fieldset")
        verbose_name_plural = _("Fieldsets")

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    def get_field(self, name) -> "FlexField":
        ff = [f for f in self.get_fields() if f.name == name]
        return ff[0]

    def get_fields(self):
        local_names = [f.name for f in self.fields.all()]
        if self.extends:
            for f in self.extends.get_fields():
                if f.name not in local_names:
                    yield f
        for f in self.fields.all():
            yield f

    def get_form(self) -> "type[FieldDefinitionForm]":
        fields: dict[str, forms.Field] = {}
        field: "FlexField"

        for field in self.get_fields():
            fld = field.get_field(label=field.name)
            fields[field.name] = fld
        form_class_attrs = {"FieldsetForm": self, **fields}
        return type(f"{self.name}FieldsetForm", (FlexForm,), form_class_attrs)

    def clean(self):
        super().clean()
        if self.extends == self:
            raise ValidationError({"extends": "Cannot extends itself"})

    # def validate(self, data):
    #     form_class = self.get_form()
    #     form: "FieldDefinitionForm" = form_class(data=data)
    #     if form.is_valid():
    #         return True
    #     else:
    #         self.errors = form.errors
    #         raise ValidationError(form.errors)
