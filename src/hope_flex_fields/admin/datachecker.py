from django.contrib import messages
from django.contrib.admin import ModelAdmin, TabularInline, register
from django.shortcuts import render

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin

from ..models import DataChecker, DataCheckerFieldset, Fieldset


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
