from django import forms
from django.core.exceptions import ValidationError

import pytest


def test_validate_attributes(db):
    from hope_flex_fields.models import FieldDefinition

    fd = FieldDefinition(
        name="IntField", field_type=forms.IntegerField, attrs={"cccc": "abc"}
    )
    fd.clean()
    assert fd.attrs == {
        "help_text": "",
        "max_value": None,
        "min_value": None,
        "required": False,
    }


def test_configuration(db):
    from hope_flex_fields.models import FieldDefinition

    fd = FieldDefinition(
        name="IntField", field_type=forms.IntegerField, attrs={"min_value": 10}
    )
    field = fd.get_field()
    with pytest.raises(ValidationError) as e:
        field.clean(1)
    assert e.value.messages == ["Ensure this value is greater than or equal to 10."]


def test_override(db):
    from hope_flex_fields.models import FieldDefinition, FlexField

    fd = FieldDefinition(
        name="IntField", field_type=forms.IntegerField, validation="true", regex=".*"
    )
    fld = FlexField(field=fd, validation="false", regex=r"\d")
    field = fld.get_field()
    with pytest.raises(ValidationError) as e:
        field.clean(1)
    assert e.value.messages == ["Please insert a valid value"]

    fld = FlexField(field=fd, regex=r"\d$")
    field = fld.get_field()
    with pytest.raises(ValidationError) as e:
        field.clean(11)
    assert e.value.messages == [r"Invalid format. Allowed Regex is '\d$'"]
