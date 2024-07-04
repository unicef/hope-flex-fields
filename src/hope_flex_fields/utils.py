import inspect

from django.utils.text import slugify


def namefy(value):
    return slugify(value).replace("-", "_")


def get_kwargs_for_field(field, extra: dict | None = None):
    sig: inspect.Signature = inspect.signature(field)
    arguments = extra or {}
    field_arguments = {
        k.name: k.default
        for __, k in sig.parameters.items()
        if k.default not in [inspect.Signature.empty]
    }
    arguments.update(field_arguments)
    return arguments
