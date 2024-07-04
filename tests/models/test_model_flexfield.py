from django import forms
from django.core.exceptions import ValidationError

import pytest

from hope_flex_fields.models import Fieldset


@pytest.fixture
def config(db):
    from testutils.factories import (
        FieldDefinitionFactory,
        FieldsetFactory,
        FlexFieldFactory,
    )

    fd1 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fd2 = FieldDefinitionFactory(field_type=forms.FloatField, attrs={"min_value": 1})
    fd3 = FieldDefinitionFactory(field_type=forms.FloatField, attrs={"required": False})
    fd4 = FieldDefinitionFactory(
        field_type=forms.IntegerField, attrs={"required": False}, regex=r"\d\d\d"
    )

    fs = FieldsetFactory()
    FlexFieldFactory(name="int", field=fd1, fieldset=fs)
    FlexFieldFactory(name="float", field=fd2, fieldset=fs)
    FlexFieldFactory(name="int1", field=fd3, fieldset=fs)
    FlexFieldFactory(name="int2", field=fd4, fieldset=fs)

    return {"fs": fs}


def test_validate_row(config):
    data = {"int": 1, "float": 1.1, "str": "string"}
    fs: Fieldset = config["fs"]

    assert fs.validate(data)


def test_validate_fail(config):
    #  try to validate json formatted data against a FieldSet
    data = {"int": 0, "float": 1.1, "str": "string"}
    fs: Fieldset = config["fs"]
    with pytest.raises(ValidationError) as e:
        fs.validate(data)

    assert e.value.message_dict == {
        "int": ["Ensure this value is greater than or equal to 1."]
    }


def test_validate_regex(config):
    #  try to validate json formatted data against a FieldSet
    data = {"int": 10, "float": 1.1, "str": "string", "int2": "1"}
    fs: Fieldset = config["fs"]
    with pytest.raises(ValidationError) as e:
        fs.validate(data)
    assert fs.errors == {"int2": ["Invalid format. Allowed Regex is '\\d\\d\\d'"]}
    assert e.value.message_dict == {
        "int2": ["Invalid format. Allowed Regex is '\\d\\d\\d'"]
    }
    data = {"int": 10, "float": 1.1, "str": "string", "int2": "111"}
    assert fs.validate(data)
