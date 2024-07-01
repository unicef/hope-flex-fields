from django import forms
from django.core.exceptions import ValidationError

import pytest

from hope_flex_fields.models import Fieldset


@pytest.fixture
def config(db):
    from hope_flex_fields.models import FieldDefinition, Fieldset, FieldsetField

    fd1 = FieldDefinition.objects.create(
        name="IntField", field_type=forms.IntegerField, attrs={"min_value": 1}
    )
    fd2 = FieldDefinition.objects.create(
        name="FloatField", field_type=forms.FloatField, attrs={"min_value": 1}
    )
    fs = Fieldset.objects.create(name="Fieldset")

    FieldsetField.objects.create(label="int", field=fd1, fieldset=fs)
    FieldsetField.objects.create(label="float", field=fd2, fieldset=fs)
    return {"fs": fs}


def test_validate_row(config):
    #  try to validate json formatted data against a FieldSet
    data = {"int": 1, "float": 1.1, "str": "string"}
    fs: Fieldset = config["fs"]

    assert fs.validate(data)


def test_validate_fail(config):
    #  try to validate json formatted data against a FieldSet
    data = {"int": 0, "float": 1.1, "str": "string"}
    fs: Fieldset = config["fs"]
    with pytest.raises(ValidationError) as e:
        fs.validate(data)
    assert e.value.messages == ["Ensure this value is greater than or equal to 1."]
