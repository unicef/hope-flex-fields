from django import forms
from django.core.exceptions import ValidationError

import pytest


def test_validate_attributes(db):
    from hope_flex_fields.models import FieldDefinition

    fd = FieldDefinition(
        name="IntField", field_type=forms.IntegerField, attrs={"cccc": "abc"}
    )
    with pytest.raises(ValidationError):
        fd.clean()


def test_configuration(db):
    from hope_flex_fields.models import FieldDefinition

    fd = FieldDefinition(
        name="IntField", field_type=forms.IntegerField, attrs={"min_value": 10}
    )
    field = fd.get_field()
    with pytest.raises(ValidationError) as e:
        field.clean(1)
    assert e.value.messages == ["Ensure this value is greater than or equal to 10."]
