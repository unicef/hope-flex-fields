import functools
import inspect
import io
import tempfile
import weakref
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING

from django import forms
from django.core.management import call_command
from django.forms.fields import DateTimeFormatsIterator
from django.utils.text import slugify

from strategy_field.utils import fqn

from hope_flex_fields.registry import field_registry

if TYPE_CHECKING:
    from hope_flex_fields.models import FieldDefinition


def namefy(value):
    return slugify(value).replace("-", "_")


def get_common_attrs():
    return {"required": False, "help_text": ""}


def get_kwargs_from_field_class(field: "str|forms.Field", extra: dict | None = None):
    field = field_registry.get_class(field)

    sig: inspect.Signature = inspect.signature(field)
    arguments = extra or {}
    field_arguments = {
        k.name: k.default for __, k in sig.parameters.items() if k.default not in [inspect.Signature.empty]
    }
    arguments.update(field_arguments)
    return arguments


def get_kwargs_from_formfield(field: forms.Field):
    from hope_flex_fields.models import FieldDefinition

    fd = FieldDefinition.objects.get(name=type(field).__name__)
    ret = {}
    for attr_name in fd.attributes.keys():
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


def dumpdata_to_buffer():
    buf = StringIO()
    call_command(
        "dumpdata",
        "hope_flex_fields",
        use_natural_primary_keys=True,
        use_natural_foreign_keys=True,
        stdout=buf,
    )
    buf.seek(0)
    return buf.getvalue()


def loaddata_from_buffer(buf):
    workdir = Path(".").absolute()
    kwargs = {
        "dir": workdir,
        "prefix": "~LOADDATA",
        "suffix": ".json",
        "delete": False,
    }
    with tempfile.NamedTemporaryFile(**kwargs) as fdst:
        fdst.write(buf.getvalue())
        fixture = (workdir / fdst.name).absolute()
    out = io.StringIO()
    try:
        call_command("loaddata", fixture, stdout=out, verbosity=3)
    except Exception:
        raise
    finally:
        fixture.unlink()
    return out.getvalue()


def create_default_fields(apps, schema_editor):
    from hope_flex_fields.registry import field_registry

    fd: "FieldDefinition" = apps.get_model("hope_flex_fields", "FieldDefinition")

    for fld in field_registry:
        name = fld.__name__
        fd.objects.get_or_create(
            name=name,
            field_type=fqn(fld),
            defaults={"attrs": get_kwargs_from_field_class(fld, get_common_attrs())},
        )


def memoized_method(*lru_args, **lru_kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapped_func(self, *args, **kwargs):
            # We're storing the wrapped method inside the instance. If we had
            # a strong reference to self the instance would never die.
            self_weak = weakref.ref(self)

            @functools.wraps(func)
            @functools.lru_cache(*lru_args, **lru_kwargs)
            def cached_method(*args, **kwargs):
                return func(self_weak(), *args, **kwargs)

            setattr(self, func.__name__, cached_method)
            return cached_method(*args, **kwargs)

        return wrapped_func

    return decorator
