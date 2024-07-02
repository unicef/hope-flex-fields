from django import forms
from django.urls import reverse

import pytest

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


@pytest.fixture
def record(db):
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
    return fs


def test_fieldset_test(app, record):
    url = reverse(f"admin:hope_flex_fields_fieldset_test", args=[record.pk])
    res = app.get(url)
    res.forms["test"]["int"] = "1"
    res = res.forms["test"].submit()
    messages = [s.message for s in res.context["messages"]]
    assert messages == ["Please correct the errors below"]

    res.forms["test"]["float"] = "1.1"
    res = res.forms["test"].submit()
    messages = [s.message for s in res.context["messages"]]
    assert messages == ["Valid"]
