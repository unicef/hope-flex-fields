from pathlib import Path

from django import forms
from django.urls import reverse

import pytest
from webtest import Upload

from hope_flex_fields.models import FieldDefinition, Fieldset


@pytest.fixture
def data(db):
    from testutils.factories import (
        FieldDefinitionFactory,
        FieldsetFactory,
        FlexFieldFactory,
    )

    fd1 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fd2 = FieldDefinitionFactory(field_type=forms.FloatField, attrs={"min_value": 1})
    fs = FieldsetFactory()
    FlexFieldFactory(name="int", field=fd1, fieldset=fs, attrs={})
    FlexFieldFactory(name="float", field=fd2, fieldset=fs, attrs={"required": True})
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
    res = res.follow()
    msgs = [m.message for m in res.context["messages"]]
    assert msgs == ["Data successfully imported."]
    assert FieldDefinition.objects.filter(name="imported-intfield").exists()
    assert FieldDefinition.objects.filter(name="imported-floatfield").exists()
    assert Fieldset.objects.filter(name="imported-fieldset").exists()


def test_import_error(db, app, data):
    url = reverse("admin:hope_flex_fields_fielddefinition_import_all")
    res = app.get(url)
    res.forms["import-form"]["file"] = Upload("data.xxx", b"{}")
    res = res.forms["import-form"].submit()
    assert res.status_code == 200
    assert res.context["form"].errors == {
        "file": ["File extension “xxx” is not allowed. Allowed extensions are: json."]
    }

    res.forms["import-form"]["file"] = Upload("data.json", b"abc")
    res = res.forms["import-form"].submit()
    assert res.status_code == 200

    assert res.context["form"].errors == {"file": ["Invalid fixture file"]}

    res.forms["import-form"]["file"] = Upload("data.json", b'{"a": 1}')
    res = res.forms["import-form"].submit()
    assert res.status_code == 302
    res = res.follow()
    assert (
        "Problem installing fixture " in [m.message for m in res.context["messages"]][0]
    )
