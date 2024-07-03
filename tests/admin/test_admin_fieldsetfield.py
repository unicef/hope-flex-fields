from django import forms
from django.urls import reverse

import pytest
from testutils.factories import (
    FieldDefinitionFactory,
    FieldsetFactory,
    FieldsetFieldFactory,
)

from hope_flex_fields.models import FieldDefinition, FieldsetField

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


@pytest.fixture
def record(db):
    fd = FieldDefinition.objects.create(
        name="IntField",
        field_type=forms.IntegerField,
        attrs={"min_value": 1, "required": True},
        regex=".*",
        validation="true",
    )
    fs1 = FieldsetFieldFactory(field=fd, name="int")

    return fs1


def test_field_test(app, record):
    url = reverse("admin:hope_flex_fields_fieldsetfield_test", args=[record.pk])
    res = app.get(url)
    res.forms["test"][record.name] = ""
    res = res.forms["test"].submit()
    messages = [s.message for s in res.context["messages"]]
    assert messages == ["Please correct the errors below"]

    res.forms["test"][record.name] = "1"
    res = res.forms["test"].submit()
    messages = [s.message for s in res.context["messages"]]
    assert messages == ["Valid"]


def test_fields_create(app):
    fd = FieldDefinitionFactory()
    fs = FieldsetFactory()
    url = reverse("admin:hope_flex_fields_fieldsetfield_add")
    res = app.get(url)
    res.form["name"] = "int"
    res.form["field"] = fd.pk
    res.form["fieldset"] = fs.pk
    res = res.form.submit()
    assert res.status_code == 302
    obj: FieldsetField = FieldsetField.objects.get(name="int")
    assert obj.attrs == {}


def test_fields_create_and_update(app, record):
    fd = FieldDefinitionFactory(field_type=forms.IntegerField)
    fs = FieldsetFactory()

    url = reverse("admin:hope_flex_fields_fieldsetfield_add")
    res = app.get(url)
    res.form["name"] = "int2"
    res.form["field"] = fd.pk
    res.form["fieldset"] = fs.pk

    res = res.form.submit("_continue").follow()
    assert res.form["attrs"].value == "{}"

    res.form["attrs"] = (
        '{"max_value": 1, "min_value": 10, ' '"required": false, "help_text": ""}'
    )
    res = res.form.submit("_continue")

    obj: FieldsetField = FieldsetField.objects.get(name="int2")
    assert obj.attrs == {
        "max_value": 1,
        "min_value": 10,
        "required": False,
        "help_text": "",
    }
