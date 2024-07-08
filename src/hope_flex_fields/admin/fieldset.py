from django import forms
from django.contrib import messages
from django.contrib.admin import ModelAdmin, register
from django.contrib.contenttypes.models import ContentType
from django.db.transaction import atomic
from django.forms import modelform_factory
from django.shortcuts import render

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin

from ..forms import FieldsetForm
from ..models import FieldDefinition, Fieldset, FlexField
from ..utils import get_kwargs_from_formfield
from .flexfield import FieldsetFieldTabularInline


class FieldSetForm(forms.Form):
    content_type = forms.ModelChoiceField(queryset=ContentType.objects.all())

    def analyse(self):
        ct: ContentType = self.cleaned_data["content_type"]
        model_class = ct.model_class()
        model_form = modelform_factory(
            model_class, exclude=(model_class._meta.pk.name,)
        )
        errors = []
        fields = []
        config = {}
        for name, field in model_form().fields.items():
            try:
                fd = FieldDefinition.objects.get(name=type(field).__name__)
                fld = FlexField(
                    name=name, field=fd, attrs=get_kwargs_from_formfield(field)
                )
                fld.attrs = fld.get_merged_attrs()
                fields.append(fld)
                config["name"] = {"definition": fd.name, "attrs": fld.attrs}
                fld.get_field()
            except FieldDefinition.DoesNotExist:
                errors.append(
                    {
                        "name": name,
                        "error": f"Field definition for '{type(field).__name__}' does not exist",
                    }
                )
        return {
            "fields": fields,
            "errors": errors,
            "config": config,
            "content_type": ct,
        }


class FieldSetForm2(forms.Form):
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.all(), widget=forms.HiddenInput
    )
    config = forms.JSONField(widget=forms.HiddenInput)

    def save(self):
        with atomic():
            ct: ContentType = self.cleaned_data["content_type"]
            model_class = ct.model_class()
            fs, __ = Fieldset.objects.get_or_create(
                name=f"{model_class._meta.app_label}_{model_class._meta.model_name}"
            )
            for name, info in self.cleaned_data["config"].items():
                fd = FieldDefinition.objects.get(name=info["definition"])
                fs.fields.get_or_create(name=name, field=fd, attrs=info["attrs"])


class inspect_field:
    pass


@register(Fieldset)
class FieldsetAdmin(ExtraButtonsMixin, ModelAdmin):
    list_select_related = True
    search_fields = ("name",)
    list_display = ("name",)
    inlines = [FieldsetFieldTabularInline]
    form = FieldsetForm

    @button()
    def create_from_content_type(self, request):
        ctx = self.get_common_context(request, title="Create from ContentType")
        if request.method == "POST":
            if "config" in request.POST:
                form = FieldSetForm2(request.POST, request.FILES)
                form.is_valid()
                form.save()
            else:
                form = FieldSetForm(request.POST, request.FILES)
                if form.is_valid():
                    result = form.analyse()
                    ctx.update(**result)
                    form = FieldSetForm2(
                        initial={
                            "content_type": result["content_type"],
                            "config": result["config"],
                        }
                    )
        else:
            form = FieldSetForm()
        ctx["form"] = form
        return render(request, "flex_fields/fieldset/analyse.html", ctx)

    @button()
    def inspect(self, request, pk):
        ctx = self.get_common_context(request, pk, title="Inspect")
        return render(request, "flex_fields/inspect.html", ctx)

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
