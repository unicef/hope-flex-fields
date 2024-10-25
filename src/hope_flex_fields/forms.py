from django import forms
from django.forms import ModelForm

from jsoneditor.forms import JSONEditor
from strategy_field.utils import fqn

from .models import FieldDefinition, Fieldset, FlexField
from .utils import get_default_attrs, get_kwargs_from_field_class
from .widgets import JavascriptEditor


class FieldDefinitionForm(ModelForm):
    validation = forms.CharField(widget=JavascriptEditor(toolbar=False), required=False)
    attrs = forms.JSONField(
        widget=JSONEditor(
            init_options={"mode": "code", "modes": ["text", "code", "tree"]},
            ace_options={"readOnly": False},
        ),
        required=True,
    )

    class Meta:
        model = FieldDefinition
        exclude = ()

    def clean(self):
        super().clean()
        if self.instance.pk:  # update
            if fqn(self.instance.field_type) != self.cleaned_data["field_type"]:
                self.cleaned_data[
                    "attrs"
                ] = get_default_attrs() | get_kwargs_from_field_class(
                    self.cleaned_data["field_type"]
                )
            else:
                self.cleaned_data["attrs"] = (
                    get_default_attrs()
                    | get_kwargs_from_field_class(self.cleaned_data["field_type"])
                    | self.cleaned_data["attrs"]
                )


class FlexFieldForm(ModelForm):
    validation = forms.CharField(widget=JavascriptEditor(toolbar=False), required=False)
    attrs = forms.JSONField(
        widget=JSONEditor(
            init_options={"mode": "code", "modes": ["text", "code", "tree"]},
            ace_options={"readOnly": False},
        ),
        required=False,
    )

    class Meta:
        model = FlexField
        exclude = ()


class FieldsetForm(ModelForm):
    class Meta:
        model = Fieldset
        exclude = ()
