from typing import TYPE_CHECKING

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from .base import TestForm
from .fieldset import Fieldset

if TYPE_CHECKING:
    from ..forms import FieldDefinitionForm
    from .field import FLexField


class DataCheckerManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class DataCheckerFieldset(models.Model):
    checker = models.ForeignKey(
        "DataChecker", on_delete=models.CASCADE, related_name="members"
    )
    fieldset = models.ForeignKey(Fieldset, on_delete=models.CASCADE)
    prefix = models.CharField(max_length=30)
    order = models.PositiveSmallIntegerField(default=0)


class DataChecker(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    fieldsets = models.ManyToManyField(Fieldset, through=DataCheckerFieldset)
    objects = DataCheckerManager()

    class Meta:
        verbose_name = _("DataChecker")
        verbose_name_plural = _("DataCheckers")

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    def get_form(self) -> "type[FieldDefinitionForm]":
        fields: dict[str, forms.Field] = {}
        field: "FLexField"
        for fs in self.members.all():
            for field in fs.fieldset.fields.filter():
                fld = field.get_field()
                fields[f"{fs.prefix}_{field.name}"] = fld
        form_class_attrs = {"DataChecker": self, **fields}
        return type(f"{self.name}DataChecker", (TestForm,), form_class_attrs)

    def validate(self, data):
        form_class = self.get_form()
        form: "FieldDefinitionForm" = form_class(data=data)
        if form.is_valid():
            return True
        else:
            self.errors = form.errors
            raise ValidationError(form.errors)

    def validate_many(self, data):
        ret = []
        for r in data:
            try:
                self.validate(r)
                ret.append("Ok")
            except ValidationError as e:
                ret.append(e.message_dict)
        return ret
