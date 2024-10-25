from django import forms
from django.contrib import messages
from django.contrib.admin import ModelAdmin, TabularInline, register
from django.shortcuts import render

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin

from ..forms import FlexFieldForm
from ..models import FieldDefinition, FlexField


class FieldsetFieldTabularInline(TabularInline):
    model = FlexField
    show_change_link = True
    fields = ("name", "field", "attrs")


@register(FlexField)
class FieldsetFieldAdmin(ExtraButtonsMixin, ModelAdmin):
    list_display = ("fieldset", "field", "name")
    list_filter = ("fieldset", "field")
    search_fields = ("name",)
    form = FlexFieldForm

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

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial["attrs"] = "{}"
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
                self.message_user(request, "Please correct the errors below", messages.ERROR)
        else:
            form = form_class()

        ctx["form"] = form
        return render(request, "flex_fields/test.html", ctx)
