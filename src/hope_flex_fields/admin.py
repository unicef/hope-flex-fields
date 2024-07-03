import io
import tempfile
from io import StringIO
from pathlib import Path

from django import forms
from django.contrib import messages
from django.contrib.admin import ModelAdmin, TabularInline, register
from django.core.management import call_command
from django.core.serializers.base import DeserializationError
from django.db.models import JSONField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from admin_extra_buttons.decorators import button, view
from admin_extra_buttons.mixins import ExtraButtonsMixin
from jsoneditor.forms import JSONEditor

from .forms import FieldDefinitionForm
from .models import (
    DataChecker,
    DataCheckerFieldset,
    FieldDefinition,
    Fieldset,
    FieldsetField,
    get_default_attrs,
)


class ImportConfigurationForm(forms.Form):
    file = forms.FileField()


@register(FieldDefinition)
class FieldDefinitionAdmin(ExtraButtonsMixin, ModelAdmin):
    list_display = ("name", "field_type_", "required", "js_validation")
    list_filter = ("field_type",)
    search_fields = ("name", "description")
    form = FieldDefinitionForm
    fieldsets = (
        ("", {"fields": (("name", "field_type"), "description")}),
        (
            "Configuration",
            {
                "classes": ("collapse", "open"),
                "fields": ("regex", "attrs", "validation"),
            },
        ),
    )
    initial = {"attrs": get_default_attrs()}

    def field_type_(self, obj):
        return obj.field_type.__name__

    def js_validation(self, obj):
        return bool(obj.validation)

    js_validation.short_description = "js"
    js_validation.boolean = True

    @view()
    def export_all(self, request):
        buf = StringIO()
        call_command(
            "dumpdata",
            "hope_flex_fields",
            use_natural_primary_keys=True,
            use_natural_foreign_keys=True,
            stdout=buf,
        )
        buf.seek(0)
        return HttpResponse(buf.getvalue(), content_type="application/json")

    @view()
    def import_all(self, request):
        ctx = self.get_common_context(request, title="Import Configuration")
        if request.method == "POST":
            form = ImportConfigurationForm(request.POST, request.FILES)
            if form.is_valid():
                workdir = Path(".").absolute()
                kwargs = {
                    "dir": workdir,
                    "prefix": "~LOADDATA",
                    "suffix": ".json",
                    "delete": False,
                }
                with tempfile.NamedTemporaryFile(**kwargs) as fdst:
                    fdst.write(form.files["file"].file.read())
                    fixture = (workdir / fdst.name).absolute()
                out = io.StringIO()
                try:
                    call_command("loaddata", fixture, stdout=out, verbosity=3)
                except DeserializationError as e:
                    self.message_user(request, str(e), messages.ERROR)
                finally:
                    fixture.unlink()
                self.message_user(request, "Data successfully imported.")
                return HttpResponseRedirect("..")
        else:
            form = ImportConfigurationForm()
        ctx["form"] = form
        return render(request, "admin/hope_flex_fields/import_config.html", ctx)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial["attrs"] = get_default_attrs()
        return initial

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
    list_filter = ("fieldset", "field")
    search_fields = ("name",)
    # form = FieldsetFieldForm
    initial = {"attrs": dict()}

    fieldsets = (
        ("", {"fields": ("name", "field", "fieldset")}),
        (
            "Overrides",
            {
                "classes": ("collapse", "open"),
                "fields": ("regex", "attrs", "validation"),
            },
        ),
    )

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
        return render(request, "flex_fields/fieldsetfield/test.html", ctx)


class DataCheckerFieldsetTabularInline(TabularInline):
    model = DataCheckerFieldset
    fields = ("fieldset", "prefix", "order")

    def get_ordering(self, request):
        return ["order"]


@register(DataChecker)
class DataCheckerAdmin(ExtraButtonsMixin, ModelAdmin):
    list_display = ("name",)
    inlines = [DataCheckerFieldsetTabularInline]

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

    @button()
    def validate(self, request, pk):
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
