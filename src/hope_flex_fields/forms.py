from django import forms
from django.forms import ModelForm

from jsoneditor.forms import JSONEditor

from .models import Fieldset
from .widgets import JavascriptEditor


class FieldsetForm(ModelForm):
    validation = forms.CharField(widget=JavascriptEditor(toolbar=False), required=False)
    attrs = forms.CharField(
        widget=JSONEditor(
            init_options={"mode": "code", "modes": ["text", "code", "tree"]},
            ace_options={"readOnly": False},
        ),
        required=False,
    )

    class Meta:
        model = Fieldset
        exclude = ()
