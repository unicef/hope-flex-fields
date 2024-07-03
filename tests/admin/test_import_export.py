from pathlib import Path

from django import forms
from django.urls import reverse

import pytest
from webtest import Upload

from hope_flex_fields.models import FieldDefinition, Fieldset


@pytest.fixture
def data(db):
    from hope_flex_fields.models import FieldDefinition, Fieldset, FieldsetField

    fd1 = FieldDefinition.objects.create(
        name="IntField", field_type=forms.IntegerField, attrs={"min_value": 1}
    )
    fd2 = FieldDefinition.objects.create(
        name="FloatField", field_type=forms.FloatField, attrs={"min_value": 1}
    )
    fs = Fieldset.objects.create(name="Fieldset")

    FieldsetField.objects.create(name="int", field=fd1, fieldset=fs)
    FieldsetField.objects.create(name="float", field=fd2, fieldset=fs)
    return fs


def test_export_all(db, app, data):
    url = reverse("admin:hope_flex_fields_fielddefinition_export_all")
    res = app.get(url)
    assert res.json


def test_import_all(db, app, data):
    url = reverse("admin:hope_flex_fields_fielddefinition_import_all")
    data = (Path(__file__).parent / "data.json").read_bytes()
    res = app.get(url)
    res.forms["import-form"]["file"] = Upload("data.json", data)
    res = res.forms["import-form"].submit()
    assert res.status_code == 302
    assert FieldDefinition.objects.filter(name="imported-intfield").exists()
    assert FieldDefinition.objects.filter(name="imported-floatfield").exists()
    assert Fieldset.objects.filter(name="imported-fieldset").exists()
