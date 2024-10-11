import json
from json import JSONDecodeError

from django import forms
from django.contrib import messages
from django.contrib.admin import ModelAdmin, register
from django.core.exceptions import ValidationError
from django.core.serializers.base import DeserializationError
from django.core.validators import FileExtensionValidator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _

from admin_extra_buttons.decorators import button, view
from admin_extra_buttons.mixins import ExtraButtonsMixin

from ..forms import FieldDefinitionForm
from ..models import FieldDefinition
from ..utils import dumpdata_to_buffer, get_default_attrs, loaddata_from_buffer


@deconstructible
class FixtureFileValidator(object):
    error_messages = {
        "invalid_json": _("Invalid fixture file"),
    }

    def __call__(self, data):
        # This is a bit expensive but we do not expect big files
        try:
            json.load(data)
            data.seek(0)
        except JSONDecodeError:
            raise ValidationError(self.error_messages["invalid_json"])


class ImportConfigurationForm(forms.Form):
    file = forms.FileField(
        validators=[
            FixtureFileValidator(),
            FileExtensionValidator(allowed_extensions=["json"]),
        ]
    )


@register(FieldDefinition)
class FieldDefinitionAdmin(ExtraButtonsMixin, ModelAdmin):
    list_display = ("name", "field_type_", "required", "js_validation")
    list_filter = ("field_type",)
    search_fields = ("name", "description")
    form = FieldDefinitionForm
    readonly_fields = ("system_data", "content_type")
    fieldsets = (
        ("", {"fields": (("name", "field_type"), "description")}),
        (
            "Configuration",
            {
                "classes": ("collapse", "open"),
                "fields": ("regex", "attrs", "validation"),
            },
        ),
        (
            "Advanced",
            {
                "classes": ("collapse", "open"),
                "fields": ("content_type", "system_data"),
            },
        ),
    )

    def field_type_(self, obj):
        return obj.field_type.__name__

    def js_validation(self, obj):
        return bool(obj.validation)

    js_validation.short_description = "js"
    js_validation.boolean = True

    @view()
    def export_all(self, request):
        data = dumpdata_to_buffer()
        return HttpResponse(data, content_type="application/json")

    @view()
    def import_all(self, request):
        ctx = self.get_common_context(request, title="Import Configuration")
        if request.method == "POST":
            form = ImportConfigurationForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    loaddata_from_buffer(form.files["file"].file)
                    self.message_user(request, "Data successfully imported.")
                except DeserializationError as e:
                    self.message_user(request, str(e), messages.ERROR)
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
        try:
            field = fd.get_field()
        except Exception as e:
            self.message_user(request, str(e))
            field = fd.get_field({})

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
        return render(request, "flex_fields/test.html", ctx)

    @button()
    def inspect(self, request, pk):
        ctx = self.get_common_context(request, pk)
        fd: FieldDefinition = ctx["original"]
        fd.set_default_arguments()
        fd.save()
