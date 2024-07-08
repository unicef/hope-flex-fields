import inspect

from django import forms
from django.forms.fields import DateTimeFormatsIterator
from django.utils.text import slugify


def namefy(value):
    return slugify(value).replace("-", "_")


def get_kwargs_from_field_class(field, extra: dict | None = None):
    sig: inspect.Signature = inspect.signature(field)
    arguments = extra or {}
    field_arguments = {
        k.name: k.default
        for __, k in sig.parameters.items()
        if k.default not in [inspect.Signature.empty]
    }
    arguments.update(field_arguments)
    return arguments


def get_kwargs_from_formfield(field: forms.Field):
    from hope_flex_fields.models import FieldDefinition

    fd = FieldDefinition.objects.get(name=type(field).__name__)
    ret = {}
    for attr_name in fd.attrs.keys():
        if attr_name in (
            "widget",
            "validators",
            "error_messages",
            "error_messages",
            "help_text",
            "label",
        ):
            continue
        value = getattr(field, attr_name)
        # if attr_name in ("help_text", "label"):
        #     value = str(value)
        if isinstance(value, DateTimeFormatsIterator):
            value = [str(v) for v in value]
        ret[attr_name] = value
    return ret
