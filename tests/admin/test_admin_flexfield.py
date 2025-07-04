from django import forms
from django.urls import reverse

import pytest
from testutils.factories import FieldDefinitionFactory, FieldsetFactory, FlexFieldFactory

from hope_flex_fields.models import FieldDefinition, FlexField

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
    return FlexFieldFactory(definition=fd, name="int")


def test_field_test(app, record):
    url = reverse("admin:hope_flex_fields_flexfield_test", args=[record.pk])
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
    url = reverse("admin:hope_flex_fields_flexfield_add")
    res = app.get(url)
    form = res.forms["flexfield_form"]
    form["name"] = "int"
    form["definition"] = fd.pk
    form["fieldset"] = fs.pk
    res = form.submit()
    assert res.status_code == 302
    obj: FlexField = FlexField.objects.get(name="int")
    assert obj.attributes == "{}"


def test_fields_create_and_update(app, record):
    fd = FieldDefinitionFactory(field_type=forms.IntegerField)
    fs = FieldsetFactory()

    url = reverse("admin:hope_flex_fields_flexfield_add")
    res = app.get(url)
    form = res.forms["flexfield_form"]
    form["name"] = "int2"
    form["definition"] = fd.pk
    form["fieldset"] = fs.pk

    res = form.submit("_continue")
    assert res.status_code == 302, res.context["adminform"].form.errors
    res = res.follow()
    form = res.forms["flexfield_form"]
    assert form["attrs"].value == '"{}"'

    form["attrs"] = '{"max_value": 1, "min_value": 10, "required": false, "help_text": ""}'
    res = form.submit("_continue")
    assert res.status_code == 302, res.context["adminform"].form.errors

    obj: FlexField = FlexField.objects.get(name="int2")
    assert obj.attributes == {
        "max_value": 1,
        "min_value": 10,
        "required": False,
        "help_text": "",
    }
