import logging
from types import GeneratorType
from typing import Iterable

from django import forms
from django.db import models

from django_regex.fields import RegexField
from django_regex.validators import RegexValidator

logger = logging.getLogger(__name__)


def get_default_attrs():
    return {"required": False, "help_text": ""}


class FlexForm(forms.Form):
    fieldset = None


class AbstractField(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=500, blank=True, null=True, default="")
    attrs = models.JSONField(default=dict, blank=True, null=False)
    regex = RegexField(blank=True, null=True, validators=[RegexValidator()])
    validation = models.TextField(blank=True, null=True, default="")

    class Meta:
        abstract = True


class ValidatorMixin:

    def validate(
        self, data: Iterable, include_success: bool = False, fail_if_alien: bool = False
    ):
        if not isinstance(data, (list, tuple, GeneratorType)):
            data = [data]
        form_class: type[FlexForm] = self.get_form()
        known_fields = set(sorted(form_class.declared_fields.keys()))
        ret = {}
        for i, row in enumerate(data, 1):
            form: "FlexForm" = form_class(data=row)
            posted_fields = set(sorted(row.keys()))
            row_errors = {}
            if fail_if_alien and (diff := posted_fields.difference(known_fields)):
                row_errors["-"] = [f"Alien values found {diff}"]
            if not form.is_valid():
                row_errors.update(**form.errors)

            if row_errors:
                ret[i] = row_errors
            elif include_success:
                ret[i] = "Ok"
        return ret
