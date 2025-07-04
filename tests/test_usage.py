from django import forms

import pytest
from testutils.factories import DataCheckerFactory, DataCheckerFieldsetFactory

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hope_flex_fields.models import DataChecker, Fieldset


@pytest.fixture
def config(db):
    from testutils.factories import FieldDefinitionFactory, FieldsetFactory, FlexFieldFactory

    fd1 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fd2 = FieldDefinitionFactory(
        field_type=forms.FloatField,
        attrs={"min_value": 1},
        validation="""if (value % 2 == 0) {result="Insert an odd number"}""",
    )
    fs = FieldsetFactory()
    FlexFieldFactory(name="int", definition=fd1, fieldset=fs, attrs={})
    FlexFieldFactory(name="float", definition=fd2, fieldset=fs, attrs={"required": True})

    dc = DataCheckerFactory()
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs, prefix="aaa_")
    return {"fs": fs, "dc": dc}


def test_validate_fs_json(config):
    fs: Fieldset = config["fs"]

    data = [
        {"int": 1, "float": 2.0},
        {"int": 2, "float": 2.2},
        {"int": -3, "float": 2.1},
    ]
    result = fs.validate(data, include_success=True)
    assert result == {
        1: {"float": ["Insert an odd number"]},
        2: "Ok",
        3: {"int": ["Ensure this value is greater than or equal to 1."]},
    }


def test_validate_dc_json(config):
    dc: DataChecker = config["dc"]
    data = [
        {"aaa_int": 1, "aaa_float": 2.0},
        {"aaa_int": 2, "aaa_float": 2.2},
        {"aaa_int": -3, "aaa_float": 2.1},
    ]
    result = dc.validate(data, include_success=True)
    assert result == {
        1: {"aaa_float": ["Insert an odd number"]},
        2: "Ok",
        3: {"aaa_int": ["Ensure this value is greater than or equal to 1."]},
    }


def test_validate_dc_exclude_success(config):
    dc: DataChecker = config["dc"]
    data = [
        {"aaa_int": 1, "aaa_float": 2.0},
        {"aaa_int": 2, "aaa_float": 2.2},
        {"aaa_int": -3, "aaa_float": 2.1},
    ]
    result = dc.validate(data)
    assert result == {
        1: {"aaa_float": ["Insert an odd number"]},
        3: {"aaa_int": ["Ensure this value is greater than or equal to 1."]},
    }


def test_validate_dc_fail_if_alien(config):
    dc: DataChecker = config["dc"]
    data = [
        {"aaa_alien": -3, "aaa_float": 2.1, "aaa_int": 0},
        {"aaa_int": -3, "aaa_float": 2.1},
    ]
    result = dc.validate(data, fail_if_alien=True)
    assert result == {
        1: {
            "-": ["Alien values found {'aaa_alien'}"],
            "aaa_int": ["Ensure this value is greater than or equal to 1."],
        },
        2: {"aaa_int": ["Ensure this value is greater than or equal to 1."]},
    }
