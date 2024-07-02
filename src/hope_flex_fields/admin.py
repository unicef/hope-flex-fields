from django import forms
from django.contrib import messages
from django.contrib.admin import ModelAdmin, TabularInline, register
from django.db.models import JSONField
from django.shortcuts import render

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from jsoneditor.forms import JSONEditor

from .forms import FieldsetForm
from .models import FieldDefinition, Fieldset, FieldsetField


@register(FieldDefinition)
class FieldDefinitionAdmin(ExtraButtonsMixin, ModelAdmin):
    list_display = ("name", "description", "field_type", "required")
    form = FieldsetForm

    @button()
    def test(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Test")
        fd: FieldDefinition = ctx["original"]
        field = fd.get_field()
        form_class_attrs = {
            fd.name: field,
        }
        form_class = type("TestFlexForm", (forms.Form,), form_class_attrs)
        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():
                self.message_user(request, "Valid", messages.SUCCESS)
            else:
                self.message_user(
                    request, "Please correct the errors below", messages.ERROR
                )
        else:
            form = form_class()

        ctx["form"] = form
        return render(request, "flex_fields/fielddefinition/test.html", ctx)

    @button()
    def inspect(self, request, pk):
        ctx = self.get_common_context(request, pk)
        fd: FieldDefinition = ctx["original"]
        fd.set_default_arguments()
        fd.save()


class FieldsetFieldTabularInline(TabularInline):
    model = FieldsetField
    fields = (
        "name",
        "field",
    )


@register(Fieldset)
class FieldsetAdmin(ExtraButtonsMixin, ModelAdmin):
    list_display = ("name",)
    inlines = [FieldsetFieldTabularInline]

    @button()
    def test(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Test")
        fs: Fieldset = ctx["original"]
        form_class = fs.get_form()
        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():
                self.message_user(request, "Valid", messages.SUCCESS)
            else:
                self.message_user(
                    request, "Please correct the errors below", messages.ERROR
                )
        else:
            form = form_class()

        ctx["form"] = form
        return render(request, "flex_fields/fieldset/test.html", ctx)


@register(FieldsetField)
class FieldsetFieldAdmin(ExtraButtonsMixin, ModelAdmin):
    list_display = ("fieldset", "field", "name")
    formfield_overrides = {
        JSONField: {
            "widget": JSONEditor(
                init_options={"mode": "code", "modes": ["text", "code", "tree"]},
                ace_options={"readOnly": False},
            )
        }
    }
