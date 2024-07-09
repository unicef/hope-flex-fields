from pathlib import Path

from django import forms

import pytest
from rest_framework.test import APIClient
from testutils.factories import DataCheckerFactory

from hope_flex_fields.utils import loaddata_from_buffer


@pytest.fixture
def data(db):
    from testutils.factories import (
        DataCheckerFieldsetFactory,
        FieldDefinitionFactory,
        FieldsetFactory,
        FlexFieldFactory,
    )

    fd1 = FieldDefinitionFactory(
        field_type=forms.IntegerField, attrs={"min_value": 1, "max_value": 100}
    )
    fd2 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fd3 = FieldDefinitionFactory(
        field_type=forms.IntegerField, attrs={"max_value": 100}
    )
    fd4 = FieldDefinitionFactory(field_type=forms.FloatField, attrs={})
    fd5 = FieldDefinitionFactory(field_type=forms.DateField, attrs={})
    fd6 = FieldDefinitionFactory(field_type=forms.BooleanField)
    fd7 = FieldDefinitionFactory(
        field_type=forms.ChoiceField,
        attrs={"choices": [["a", "a"], ["b", "b"], ["c", "c"]]},
    )
    fs = FieldsetFactory()
    FlexFieldFactory(name="int1", field=fd1, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="int2", field=fd2, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="int3", field=fd3, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="float", field=fd4, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="date", field=fd5, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="bool", field=fd6, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="choice", field=fd7, fieldset=fs, attrs={"required": False})

    dc = DataCheckerFactory()
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs, prefix="fs")
    return dc


def test_fields(admin_user, data):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    response = client.get("http://testserver/api/field/")
    assert response.json()


def test_flexfield(admin_user, data):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    response = client.get("http://testserver/api/flexfield/")
    assert response.json()


def test_fieldsets(admin_user, data):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    response = client.get("http://testserver/api/fieldset/")
    assert response.json()


def test_datachecker(admin_user, data):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    response = client.get("http://testserver/api/datachecker/")
    assert response.json()


def test_sync(admin_user, data, mocked_responses):
    data = (Path(__file__).parent / "admin/data.json").read_text()

    client = APIClient()
    client.force_authenticate(user=admin_user)

    mocked_responses.get("http://testserver/api/sync/", json=data)
    response = client.get("http://testserver/api/sync/")
    out = loaddata_from_buffer(response)
    assert "Processed 33 object(s).\nInstalled 33 object(s) from 1 fixture(s)" in out
