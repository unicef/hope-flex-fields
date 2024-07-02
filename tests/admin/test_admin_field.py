from django import forms
from django.urls import reverse

import pytest

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


@pytest.fixture
def record(db):
    from hope_flex_fields.models import FieldDefinition

    fd1 = FieldDefinition.objects.create(
        name="IntField",
        field_type=forms.IntegerField,
        attrs={"min_value": 1, "required": True},
    )

    return fd1


def test_fieldset_test(app, record):
    url = reverse("admin:hope_flex_fields_fielddefinition_test", args=[record.pk])
    res = app.get(url)
    res.forms["test"]["IntField"] = ""
    res = res.forms["test"].submit()
    messages = [s.message for s in res.context["messages"]]
    assert messages == ["Please correct the errors below"]

    res.forms["test"]["IntField"] = "1"
    res = res.forms["test"].submit()
    messages = [s.message for s in res.context["messages"]]
    assert messages == ["Valid"]
