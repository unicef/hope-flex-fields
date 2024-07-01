import inspect

from django import forms
from django.contrib.admin import ModelAdmin, register
from django.db.models import JSONField
from django.shortcuts import render

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from jsoneditor.forms import JSONEditor

from hope_flex_fields.models import FieldDefinition, Fieldset, FieldsetField


@register(FieldDefinition)
class FieldDefinitionAdmin(ExtraButtonsMixin, ModelAdmin):
    list_display = ("name", "description", "field_type", "required")
    formfield_overrides = {
        JSONField: {
            "widget": JSONEditor(
                init_options={"mode": "code", "modes": ["text", "code", "tree"]},
                ace_options={"readOnly": False},
            )
        }
    }

    @button()
    def test(self, request, pk):
        ctx = self.get_common_context(request, pk)
        fd: FieldDefinition = ctx["original"]
        field = fd.get_field()
        form_class_attrs = {
            fd.name: field,
        }
        flexForm = type("TestFlexForm", (forms.Form,), form_class_attrs)
        ctx["form"] = flexForm
        return render(request, "flex_fields/test.html", ctx)

    @button()
    def inspect(self, request, pk):
        ctx = self.get_common_context(request, pk)
        fd: FieldDefinition = ctx["original"]
        stored = fd.attrs or {}
        sig: inspect.Signature = inspect.signature(fd.field_type)
        defaults = {
            k.name: k.default
            for __, k in sig.parameters.items()
            if k.default not in [inspect.Signature.empty]
        }
        defaults.update(**stored)
        fd.attrs = defaults
        fd.save()


@register(Fieldset)
class FieldsetAdmin(ExtraButtonsMixin, ModelAdmin):
    list_display = ("name",)


@register(FieldsetField)
class FieldsetFieldAdmin(ExtraButtonsMixin, ModelAdmin):
    list_display = ("fieldset", "field", "label")
