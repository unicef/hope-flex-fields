from typing import TYPE_CHECKING

from django import forms
from django.core.exceptions import ValidationError

import pytest
from testutils.factories import (
    FieldDefinitionFactory,
    FieldsetFactory,
    FlexFieldFactory,
)

from hope_flex_fields.models import Fieldset

if TYPE_CHECKING:
    from hope_flex_fields.models import FlexField


@pytest.fixture
def config(db):
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

    ret = fs.validate(data, include_success=False)
    assert ret == {}


def test_validate_fail(config):
    #  try to validate json formatted data against a FieldSet
    data = {"int": 0, "float": 1.1, "str": "string"}
    fs: Fieldset = config["fs"]
    # with pytest.raises(ValidationError) as e:
    ret = fs.validate(data)

    assert ret == {1: {"int": ["Ensure this value is greater than or equal to 1."]}}


def test_validate_regex(config):
    #  try to validate json formatted data against a FieldSet
    data = {"int": 10, "float": 1.1, "str": "string", "int2": "1"}
    fs: Fieldset = config["fs"]
    ret = fs.validate(data)
    assert ret == {1: {"int2": ["Invalid format. Allowed Regex is '\\d\\d\\d'"]}}
    data = {"int": 10, "float": 1.1, "str": "string", "int2": "111"}
    ret = fs.validate(data)
    assert ret == {}


def test_extends(config):
    fs: Fieldset = config["fs"]
    fs2 = FieldsetFactory(extends=fs)

    ii: FlexField = fs2.get_field("int")  # NOTE: we get 'int' from fs2
    assert ii.get_field().min_value == 1

    assert [f.name for f in fs2.get_fields()] == ["int", "float", "int1", "int2"]
    # add new field
    FlexFieldFactory(name="int2.1", fieldset=fs2)
    assert [f.name for f in fs2.get_fields()] == [
        "int",
        "float",
        "int1",
        "int2",
        "int2.1",
    ]

    # override existing field
    FlexFieldFactory(
        name=ii.name,
        field__field_type=ii.field.field_type,
        fieldset=fs2,
        attrs={"min_value": 100},
    )
    assert [f.name for f in fs2.get_fields()] == [
        "float",
        "int1",
        "int2",
        "int2.1",
        "int",
    ]
    ii = fs2.get_field("int")
    assert ii.get_field().min_value == 100


def test_cannot_extends_self(config):
    fs: Fieldset = config["fs"]
    fs.extends = fs
    pytest.raises(ValidationError, fs.clean)
