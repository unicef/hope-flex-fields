from pathlib import Path

from django import forms
from django.contrib import messages
from django.contrib.admin import ModelAdmin, TabularInline, register
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin

from ..file_handlers import HANDLERS
from ..models import DataChecker, DataCheckerFieldset, Fieldset
from ..models.datachecker import create_xls_importer


@deconstructible
class ValidatableFileValidator(object):
    error_messages = {
        "invalid_file": _("Unsupported file format '%s'"),
    }

    def __call__(self, f):
        if Path(f.name).suffix not in HANDLERS.keys():
            raise ValidationError(self.error_messages["invalid_file"] % Path(f.name).suffix)


class FileForm(forms.Form):
    include_success = forms.BooleanField(required=False)
    fail_if_alien = forms.BooleanField(required=False)
    file = forms.FileField(
        validators=[
            ValidatableFileValidator(),
        ]
    )


class DataCheckerFieldsetFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        all_fields = set()
        fs: Fieldset
        for form in self.forms:
            if fs := form.cleaned_data.get("fieldset"):
                prefix: str = form.cleaned_data["prefix"]
                # fs_fields = {f"{prefix}{f}" for f in fs.get_fieldnames()}
                if "%s" in prefix:
                    fs_fields = {prefix % f for f in fs.get_fieldnames()}
                else:
                    fs_fields = {f"{prefix}{f}" for f in fs.get_fieldnames()}
                if all_fields.intersection(fs_fields):
                    raise forms.ValidationError("Field names are not unique")
                all_fields.update(fs_fields)


class DataCheckerFieldsetTabularInline(TabularInline):
    model = DataCheckerFieldset
    formset = DataCheckerFieldsetFormset
    fields = ("fieldset", "prefix", "order")

    def get_ordering(self, request):
        return ["order"]


@register(DataChecker)
class DataCheckerAdmin(ExtraButtonsMixin, ModelAdmin):
    list_display = ("name",)
    inlines = [DataCheckerFieldsetTabularInline]

    @button()
    def inspect(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Inspect")
        return render(request, "flex_fields/inspect.html", ctx)

    @button()
    def validate(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Validate file")
        if request.method == "POST":
            form = FileForm(request.POST, request.FILES)
            if form.is_valid():
                dc: DataChecker = ctx["original"]
                f = form.cleaned_data["file"]
                parser = HANDLERS[Path(f.name).suffix]
                ret = dc.validate(parser(f), include_success=True)
                ctx["results"] = ret
                self.message_user(request, "Data looks valid", messages.SUCCESS)
            else:
                self.message_user(request, "Some data did not validate", messages.ERROR)

        else:
            form = FileForm()
        ctx["form"] = form
        return render(request, "flex_fields/datachecker/validate.html", ctx)

    @button()
    def create_xls_importer(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Inspect")
        dc: DataChecker = ctx["original"]
        buffer, __ = create_xls_importer(dc)
        return HttpResponse(
            buffer.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        # return render(request, "flex_fields/datachecker/inspect.html", ctx)

    @button()
    def test(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Test")
        dc: DataChecker = ctx["original"]
        form_class = dc.get_form_class()
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
