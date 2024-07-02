from django import forms

import pytest

from hope_flex_fields.importers import validate_json
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
    data = [
        {"int": 1, "float": 1.1},
        {"int": 2, "float": 2.1},
        {"int": -3, "float": 2.1},
    ]
    return {"fs": fs, "data": data}


def test_validate_json(config):
    fs: Fieldset = config["fs"]
    result = validate_json(config["data"], fs.name)
    assert result == [
        "Ok",
        "Ok",
        {"int": ["Ensure this value is greater than or equal to 1."]},
    ]
