from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

import pytest
from testutils.factories import FieldDefinitionFactory, FieldsetFactory, FlexFieldFactory

from hope_flex_fields.models import Fieldset

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


@pytest.fixture
def record(db):
    fd1 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fd2 = FieldDefinitionFactory(field_type=forms.FloatField, attrs={"min_value": 1})
    fs = FieldsetFactory()
    FlexFieldFactory(name="int", definition=fd1, fieldset=fs, attrs={})
    FlexFieldFactory(name="float", definition=fd2, fieldset=fs, attrs={"required": True})
    return fs


@pytest.fixture
def record2(db):
    ct = ContentType.objects.get_for_model(User)
    return Fieldset.objects.create_from_content_type("Test", ct)


def test_detect_changes(app, record2):
    url = reverse("admin:hope_flex_fields_fieldset_detect_changes", args=[record2.pk])
    app.get(url)


def test_fieldset_test(app, record):
    url = reverse("admin:hope_flex_fields_fieldset_test", args=[record.pk])
    res = app.get(url)
    res.forms["test"]["int"] = "1"
    res = res.forms["test"].submit()
    messages = [s.message for s in res.context["messages"]]
    assert messages == ["Please correct the errors below"]

    res.forms["test"]["float"] = "1.1"
    res = res.forms["test"].submit()
    messages = [s.message for s in res.context["messages"]]
    assert messages == ["Valid"]


def test_fieldset_unique_name(app, record):
    url = reverse("admin:hope_flex_fields_fieldset_add")
    res = app.get(url)
    res.forms["fieldset_form"]["name"] = record.name
    res = res.forms["fieldset_form"].submit()
    assert res.status_code == 200
    assert b"Fieldset with this Name already exists." in res.content


@pytest.mark.parametrize(
    "model_class",
    [
        User,
    ],
)
def test_fieldset_create_from_content_type(app, record, model_class):
    url = reverse("admin:hope_flex_fields_fieldset_create_from_content_type")
    res = app.get(url)
    res.forms["analyse-form"]["name"] = record.name
    res = res.forms["analyse-form"].submit("analyse")
    assert res.status_code == 200
    res.forms["analyse-form"]["name"] = "FS #1"
    res.forms["analyse-form"]["content_type"] = ContentType.objects.get_for_model(model_class).pk
    res = res.forms["analyse-form"].submit("analyse")

    res.forms["create-form"].submit("create")
    fs = Fieldset.objects.filter(name="FS #1").first()
    assert fs
    assert fs.fields.exists()
