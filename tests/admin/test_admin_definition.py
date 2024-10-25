from django import forms
from django.urls import reverse

import pytest
from strategy_field.utils import fqn
from testutils.factories import FieldDefinitionFactory

from hope_flex_fields.models import FieldDefinition

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


@pytest.fixture
def record(db):
    fd1 = FieldDefinitionFactory(
        name="IntField",
        field_type=forms.IntegerField,
        attrs={"min_value": 1, "required": True},
        regex=".*",
        validation="true",
    )

    return fd1


def test_field_test(app, record):
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


def test_fields_create(app, record):
    url = reverse("admin:hope_flex_fields_fielddefinition_add")
    res = app.get(url)
    form = res.forms["fielddefinition_form"]
    form["name"] = "int"
    form["field_type"] = fqn(forms.ChoiceField)
    res = form.submit()
    assert res.status_code == 302
    obj: FieldDefinition = FieldDefinition.objects.get(name="int")
    assert obj.attributes == {"choices": [], "required": False, "help_text": ""}


def test_fields_create_and_update(app, record):
    url = reverse("admin:hope_flex_fields_fielddefinition_add")
    res = app.get(url)
    form = res.forms["fielddefinition_form"]
    form["name"] = "Int"
    form["field_type"] = fqn(forms.IntegerField)
    res = form.submit("_continue").follow()
    form = res.forms["fielddefinition_form"]
    assert form["attrs"].value == (
        '{"max_value": null, "min_value": null, "step_size": null, '
        '"required": false, "help_text": ""}'
    )
    form["attrs"] = (
        '{"max_value": 1, "min_value": 10, ' '"required": false, "help_text": ""}'
    )
    form.submit("_continue").follow()

    obj: FieldDefinition = FieldDefinition.objects.get(name="Int")
    assert obj.attributes == {
        "max_value": 1,
        "min_value": 10,
        "required": False,
        "help_text": "",
        "step_size": None,
    }


def test_fields_change_type(app, record):
    url = reverse("admin:hope_flex_fields_fielddefinition_change", args=[record.pk])
    res = app.get(url)
    form = res.forms["fielddefinition_form"]
    form["name"] = "Char"
    form["field_type"] = fqn(forms.CharField)
    res = form.submit("_continue")
    assert res.status_code == 302
    obj: FieldDefinition = FieldDefinition.objects.get(name="Char")
    assert obj.attributes == {
        "empty_value": "",
        "strip": True,
        "max_length": None,
        "min_length": None,
        "required": False,
        "help_text": "",
    }
