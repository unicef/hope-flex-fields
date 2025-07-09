import json

from django import forms
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import ModelForm

from jsoneditor.forms import JSONEditor
from strategy_field.utils import fqn

from .models import DataCheckerFieldset, FieldDefinition, Fieldset, FlexField
from .registry import field_registry
from .utils import get_common_attrs, get_kwargs_from_field_class
from .widgets import JavascriptEditor


class FlexForm(forms.Form):
    fieldset = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_bound:
            self.initialize_parent_child(self.data)
        elif self.initial:
            self.initialize_parent_child(self.initial)

    def clean(self):
        super().clean()
        self.cleaned_data = json.loads(json.dumps(self.cleaned_data, cls=DjangoJSONEncoder))
        return self.cleaned_data

    def initialize_parent_child(self, data: dict) -> None:
        for field in self.fields.values():
            if field.flex_field.master and hasattr(field, "validate_with_parent"):
                parent_value = data.get(field.flex_field.master.name)
                field.choices = field.get_choices_for_parent_value(parent_value)


class FieldDefinitionForm(ModelForm):
    validation = forms.CharField(widget=JavascriptEditor(toolbar=False), required=False)

    class Meta:
        model = FieldDefinition
        fields = ("name", "description", "regex", "validation")

    def clean(self):
        super().clean()
        if not (ft := self.cleaned_data.get("field_type")) or ft not in field_registry:
            raise ValidationError({"field_type": "Invalid field type"})
        if (
            self.instance.pk
            and self.instance.field_type
            and fqn(self.instance.field_type) != self.cleaned_data["field_type"]
        ):
            self.instance.attrs = get_common_attrs() | get_kwargs_from_field_class(self.cleaned_data["field_type"])
        return self.cleaned_data


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
        fields = (
            "name",
            "description",
            "attrs",
            "regex",
            "validation",
            "fieldset",
            "definition",
            "master",
        )


class FieldsetForm(ModelForm):
    class Meta:
        model = Fieldset
        fields = (
            "name",
            "description",
            "extends",
            "content_type",
        )


class DataCheckerFieldsetForm(ModelForm):
    class Meta:
        model = DataCheckerFieldset
        fields = ("fieldset", "prefix", "order", "group", "override_group_default_value")
        widgets = {
            "group": forms.TextInput(attrs={"placeholder": "Enter group name or leave empty for root"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["override_group_default_value"].help_text = "Check to override the fieldset default group"
        self.fields["group"].help_text = "Group name to use when override is checked. Leave empty for root level."
