import logging
from typing import TYPE_CHECKING, Any, Optional, TypedDict

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import modelform_factory
from django.utils.translation import gettext as _

from deepdiff import DeepDiff

from ..utils import get_kwargs_from_formfield
from .base import FlexForm, ValidatorMixin

if TYPE_CHECKING:
    from ..models import FlexField

ContentTypeConfig = TypedDict(
    "ContentTypeConfig",
    {
        "fields": list,
        "errors": list,
        "config": dict[str, Any],
        "content_type": type[ContentType],
    },
)
# {
#             "fields": fields,
#             "errors": errors,
#             "config": config,
#             "content_type": ct,
#         }

logger = logging.getLogger(__name__)


class FieldsetManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

    def inspect_content_type(self, ct: ContentType) -> ContentTypeConfig:
        from hope_flex_fields.models import FieldDefinition, FlexField

        model_class = ct.model_class()
        model_form = modelform_factory(
            model_class, exclude=(model_class._meta.pk.name,)
        )
        errors = []
        fields = []
        config = {}
        for name, field in model_form().fields.items():
            try:
                fd = FieldDefinition.objects.get(name=type(field).__name__)
                fld = FlexField(
                    name=name, field=fd, attrs=get_kwargs_from_formfield(field)
                )
                fld.attrs = fld.get_merged_attrs()
                fld.get_field()
                config[name] = {"definition": fd.name, "attrs": fld.attrs}
                fields.append(fld)
            except FieldDefinition.DoesNotExist:
                errors.append(
                    {
                        "name": name,
                        "error": f"Field definition for '{type(field).__name__}' does not exist",
                    }
                )
            except Exception as e:
                logger.exception(e)
                errors.append(
                    {
                        "name": name,
                        "error": f"Unable to create field {name}",
                    }
                )
        return {
            "fields": fields,
            "errors": errors,
            "config": config,
            "content_type": ct,
        }

    def create_from_content_type(
        self, name: str, content_type: ContentType, config: Optional[dict] = None
    ) -> "Fieldset":
        from hope_flex_fields.models import FieldDefinition, Fieldset

        if config is None:
            inspection = Fieldset.objects.inspect_content_type(content_type)
            config = inspection["config"]
        fs, __ = Fieldset.objects.get_or_create(name=name, content_type=content_type)
        for name, info in config.items():
            fd = FieldDefinition.objects.get(name=info["definition"])
            fs.fields.get_or_create(name=name, field=fd, attrs=info["attrs"])
        return fs


class Fieldset(ValidatorMixin, models.Model):
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    extends = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, blank=True, null=True
    )

    objects = FieldsetManager()

    class Meta:
        verbose_name = _("Fieldset")
        verbose_name_plural = _("Fieldsets")

    def __str__(self):
        return self.name

    def diff_content_type(self) -> dict:
        attrs = Fieldset.objects.inspect_content_type(self.content_type)
        result = {}
        for field_name, w in attrs["config"].items():
            if ff := self.get_field(field_name):
                dd = DeepDiff(ff.attrs, w["attrs"])
                if dd:
                    result[field_name] = dd
        return result

    def natural_key(self):
        return (self.name,)

    def get_field(self, name) -> "FlexField":
        ff = [f for f in self.get_fields() if f.name == name]
        return ff[0] if ff else None

    def get_fieldnames(self):
        return [f.name for f in self.get_fields()]

    def get_fields(self):
        local_names = [f.name for f in self.fields.all()]
        if self.extends:
            for f in self.extends.get_fields():
                if f.name not in local_names:
                    yield f
        for f in self.fields.all():
            yield f

    def get_form(self) -> "type":
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
