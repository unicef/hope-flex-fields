from django.contrib import messages
from django.contrib.admin import ModelAdmin, register
from django.shortcuts import render

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin

from ..forms import FieldsetForm
from ..models import Fieldset
from .flexfield import FieldsetFieldTabularInline


@register(Fieldset)
class FieldsetAdmin(ExtraButtonsMixin, ModelAdmin):
    list_select_related = True
    search_fields = ("name",)
    list_display = ("name",)
    inlines = [FieldsetFieldTabularInline]
    form = FieldsetForm

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
