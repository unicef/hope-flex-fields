from django import forms
from django.urls import reverse

import pytest
from testutils.factories import DataCheckerFactory

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


@pytest.fixture
def record(db):
    from testutils.factories import (
        DataCheckerFieldsetFactory,
        FieldDefinitionFactory,
        FieldsetFactory,
        FlexFieldFactory,
    )

    fd1 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fd2 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fs1 = FieldsetFactory()
    fs2 = FieldsetFactory()
    FlexFieldFactory(name="int1", field=fd1, fieldset=fs1, attrs={"required": False})
    FlexFieldFactory(name="int2", field=fd2, fieldset=fs2, attrs={"required": True})

    dc = DataCheckerFactory()
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs1, prefix="fs1")
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs2, prefix="fs2")
    return dc


@pytest.fixture
def dc(db):
    from testutils.factories import (
        DataCheckerFieldsetFactory,
        FieldDefinitionFactory,
        FieldsetFactory,
        FlexFieldFactory,
    )

    fd1 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fd2 = FieldDefinitionFactory(field_type=forms.FloatField, attrs={"min_value": 1})
    fd3 = FieldDefinitionFactory(field_type=forms.DateField, attrs={"min_value": 1})
    fd4 = FieldDefinitionFactory(field_type=forms.BooleanField)
    fd5 = FieldDefinitionFactory(
        field_type=forms.ChoiceField,
        attrs={"choices": [["a", "a"], ["b", "b"], ["c", "c"]]},
    )
    fs = FieldsetFactory()
    FlexFieldFactory(name="int", field=fd1, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="float", field=fd2, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="date", field=fd3, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="bool", field=fd4, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="choice", field=fd5, fieldset=fs, attrs={"required": False})

    dc = DataCheckerFactory()
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs, prefix="fs")
    return dc


def test_datachecker_test(app, record):
    url = reverse("admin:hope_flex_fields_datachecker_test", args=[record.pk])
    res = app.get(url)
    res.forms["test"]["fs1_int1"] = ""
    res = res.forms["test"].submit()
    messages = [s.message for s in res.context["messages"]]
    assert messages == ["Please correct the errors below"]

    res.forms["test"]["fs2_int2"] = "1"
    res = res.forms["test"].submit()
    messages = [s.message for s in res.context["messages"]]
    assert messages == ["Valid"]


def test_datachecker_inspect(app, record):
    url = reverse("admin:hope_flex_fields_datachecker_inspect", args=[record.pk])
    res = app.get(url)
    assert res


def test_datachecker_xls_importer(app, dc):
    url = reverse(
        "admin:hope_flex_fields_datachecker_create_xls_importer", args=[dc.pk]
    )
    res = app.get(url)
    from pathlib import Path

    with Path("aaaa.xlsx").open("wb") as f:
        f.write(res.body)
