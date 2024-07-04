from django.contrib import messages
from django.contrib.admin import ModelAdmin, TabularInline, register
from django.http import HttpResponse
from django.shortcuts import render

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin

from ..models import DataChecker, DataCheckerFieldset, Fieldset
from ..models.datachecker import create_xls_importer


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
    def inspect(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Inspect")
        return render(request, "flex_fields/datachecker/inspect.html", ctx)

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
        return render(request, "flex_fields/test.html", ctx)
