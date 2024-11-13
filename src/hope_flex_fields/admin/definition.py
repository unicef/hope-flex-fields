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
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _

from admin_extra_buttons.decorators import button, view
from admin_extra_buttons.mixins import ExtraButtonsMixin
from jsoneditor.forms import JSONEditor

from ..forms import FieldDefinitionForm
from ..models import FieldDefinition
from ..utils import dumpdata_to_buffer, get_common_attrs, get_kwargs_from_field_class, loaddata_from_buffer


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


class ConfigurationForm(forms.Form):
    attrs = forms.JSONField(
        widget=JSONEditor(
            init_options={"mode": "code", "modes": ["text", "code", "tree"]},
            ace_options={"readOnly": False},
        ),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.instance: FieldDefinition = kwargs.pop("instance")
        super().__init__(*args, **kwargs)

    def clean(self):
        value = self.cleaned_data["attrs"]
        value = self.instance.get_default_attributes() | value
        self.cleaned_data["attrs"] = value
        return self.cleaned_data

    def save(self):
        self.instance.attrs = self.cleaned_data["attrs"]
        self.instance.save(update_fields=["attrs"])


@register(FieldDefinition)
class FieldDefinitionAdmin(ExtraButtonsMixin, ModelAdmin):
    list_display = ("name", "field_type_", "required", "js_validation", "validated")
    list_filter = ("field_type",)
    search_fields = ("name", "description")
    form = FieldDefinitionForm
    readonly_fields = ("system_data", "content_type", "validated")
    fieldsets = (
        (
            "",
            {"fields": (("name", "field_type", "validated"), ("attributes_strategy",), "description")},
        ),
        # (
        #     "Configuration",
        #     {
        #         "classes": ("collapse", "open"),
        #         "fields": ("regex", "attrs", "validation"),
        #     },
        # ),
        (
            "Advanced",
            {
                "classes": ("collapse", "open"),
                "fields": ("content_type", "system_data"),
            },
        ),
    )

    def field_type_(self, obj):
        try:
            return obj.field_type.__name__
        except AttributeError:
            return "--"

    def js_validation(self, obj):
        return bool(obj.validation)

    js_validation.short_description = "js"
    js_validation.boolean = True

    def save_model(self, request, obj, form, change):
        if not change:
            form.cleaned_data["attrs"] = get_common_attrs() | get_kwargs_from_field_class(
                form.cleaned_data["field_type"]
            )
        super().save_model(request, obj, form, change)

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

    # def get_changeform_initial_data(self, request):
    #     initial = super().get_changeform_initial_data(request)
    #     # initial["attrs"] = get_default_attrs()
    #     return initial

    @button()
    def configure(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Configure")
        if request.method == "POST":
            form1 = ConfigurationForm(request.POST, instance=self.object, prefix="fld")
            form2 = self.object.attributes_strategy.config_class(
                request.POST,
                initial=self.object.strategy_config,
                instance=self.object,
                prefix="stg",
            )
            if form1.is_valid() and form2.is_valid():
                form1.save()
                form2.save()
                self.object.refresh_from_db()
                try:
                    self.object.get_field()
                    self.object.validated = True
                except ValidationError as e:
                    self.message_user(request, str(e), messages.ERROR)
                    self.object.validated = False
                self.object.save()

                self.message_user(request, "Configuration successfully saved.")
                return HttpResponseRedirect(
                    reverse(
                        "admin:hope_flex_fields_fielddefinition_change",
                        args=[self.object.id],
                    )
                )
        else:
            form1 = ConfigurationForm(instance=self.object, initial={"attrs": self.object.attrs}, prefix="fld")
            form2 = self.object.attributes_strategy.config_class(
                instance=self.object, initial=self.object.strategy_config, prefix="stg"
            )

        ctx["form1"] = form1
        ctx["form2"] = form2
        return render(request, "flex_fields/fielddefinition/configure.html", ctx)

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
                self.message_user(request, "Please correct the errors below", messages.ERROR)
        else:
            form = form_class()

        ctx["form"] = form
        return render(request, "flex_fields/test.html", ctx)
