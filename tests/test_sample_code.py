# mypy: disable-error-code="no-untyped-def"
from django import forms

from hope_flex_fields.models import Fieldset
from hope_flex_fields.models.definition import FieldDefinition
from hope_flex_fields.models.flexfield import FlexField


def test_sample_code(db):
    data = [
        {"name": "John", "last_name": "Doe", "gender": "M", "unknown": "??"},
        {"name": "Jane", "last_name": "Doe", "gender": "F"},
        {"name": "Andrea", "last_name": "Doe", "gender": "X"},
        {"name": "Mary", "last_name": "Doe", "gender": "1"},
    ]

    fs, __ = Fieldset.objects.get_or_create(name="test.xlsx")

    charfield = FieldDefinition.objects.get(field_type=forms.CharField)
    choicefield = FieldDefinition.objects.get(field_type=forms.ChoiceField)

    FlexField.objects.get_or_create(name="name", fieldset=fs, field=charfield)
    FlexField.objects.get_or_create(name="last_name", fieldset=fs, field=charfield)
    FlexField.objects.get_or_create(
        name="gender",
        fieldset=fs,
        field=choicefield,
        attrs={"choices": [["M", "M"], ["F", "F"], ["X", "X"]]},
    )

    errors = fs.validate(data)
    assert errors == {4: {"gender": ["Select a valid choice. 1 is not one of the available choices."]}}

    errors = fs.validate(data, fail_if_alien=True)
    assert errors == {
        1: {"-": ["Alien values found {'unknown'}"]},
        4: {"gender": ["Select a valid choice. 1 is not one of the available choices."]},
    }
