from django import forms
from django.forms import ModelForm

from jsoneditor.forms import JSONEditor

from .models import FieldDefinition, Fieldset, FlexField
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
