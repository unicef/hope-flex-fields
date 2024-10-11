from django import forms
from django.contrib import messages
from django.contrib.admin import ModelAdmin, register
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.shortcuts import render

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin

from ..forms import FieldsetForm
from ..models import Fieldset
from .flexfield import FieldsetFieldTabularInline


class FieldSetForm(forms.Form):
    name = forms.CharField()
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.all(), required=True
    )

    def clean_name(self):
        if Fieldset.objects.filter(name__iexact=self.cleaned_data["name"]).exists():
            raise ValidationError("Fieldset with this name already exists")
        return self.cleaned_data["name"]

    def save(self):
        ct: ContentType = self.cleaned_data["content_type"]
        return Fieldset.objects.inspect_content_type(ct)


class FieldSetForm2(forms.Form):
    name = forms.CharField(widget=forms.HiddenInput)
    config = forms.JSONField(widget=forms.HiddenInput)
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.all(), widget=forms.HiddenInput
    )

    def save(self):
        with atomic():
            return Fieldset.objects.create_from_content_type(**self.cleaned_data)


class inspect_field:
    pass


@register(Fieldset)
class FieldsetAdmin(ExtraButtonsMixin, ModelAdmin):
    list_select_related = True
    search_fields = ("name",)
    list_display = ("name", "extends", "content_type")
    list_filter = ("content_type",)
    inlines = [FieldsetFieldTabularInline]
    form = FieldsetForm

    @button()
    def create_from_content_type(self, request):
        ctx = self.get_common_context(request, title="Create from ContentType")
        if request.method == "POST":
            if "analyse" in request.POST:
                form = FieldSetForm(request.POST, request.FILES)
                if form.is_valid():
                    result = form.save()
                    ctx.update(**result)
                    form = FieldSetForm2(
                        initial={
                            "content_type": result["content_type"],
                            "name": form.cleaned_data["name"],
                            "config": result["config"],
                        },
                    )
            else:
                # elif "create" in request.POST:
                form = FieldSetForm2(request.POST, request.FILES)
                form.is_valid()
                form.save()
                return HttpResponseRedirect("..")
        else:
            form = FieldSetForm()
        ctx["form"] = form
        return render(request, "flex_fields/fieldset/analyse.html", ctx)

    @button()
    def inspect(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Inspect")
        return render(request, "flex_fields/inspect.html", ctx)

    @button(enabled=lambda s: s.context["original"].content_type)
    def detect_changes(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Differences")
        fs: Fieldset = ctx["original"]
        ctx["diff"] = fs.diff_content_type()
        return render(request, "flex_fields/fieldset/diff.html", ctx)

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
