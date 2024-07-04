import logging

from django import forms
from django.db import models

from django_regex.fields import RegexField
from django_regex.validators import RegexValidator

logger = logging.getLogger(__name__)


def get_default_attrs():
    return {"required": False, "help_text": ""}


class TestForm(forms.Form):
    fieldset = None


class AbstractField(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=500, blank=True, null=True, default="")
    attrs = models.JSONField(default=dict, blank=True, null=False)
    regex = RegexField(blank=True, null=True, validators=[RegexValidator()])
    validation = models.TextField(blank=True, null=True, default="")

    class Meta:
        abstract = True
