from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

import pytest
from testutils.factories import (
    FieldDefinitionFactory,
    FieldsetFactory,
    FlexFieldFactory,
)

from hope_flex_fields.models import Fieldset

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


@pytest.fixture
def record(db):
    fd1 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fd2 = FieldDefinitionFactory(field_type=forms.FloatField, attrs={"min_value": 1})
    fs = FieldsetFactory()
    FlexFieldFactory(name="int", field=fd1, fieldset=fs, attrs={})
    FlexFieldFactory(name="float", field=fd2, fieldset=fs, attrs={"required": True})
    return fs


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


@pytest.mark.parametrize(
    "model_class",
    [
        User,
    ],
)
def test_fieldset_create_from_content_type(app, model_class):
    url = reverse("admin:hope_flex_fields_fieldset_create_from_content_type")
    res = app.get(url)
    res = res.forms["analyse-form"].submit()
    assert res.status_code == 200
    res.forms["analyse-form"]["content_type"] = ContentType.objects.get_for_model(
        model_class
    ).pk
    res = res.forms["analyse-form"].submit()
    res.forms["create-form"].submit()
    fs = Fieldset.objects.filter(
        name=f"{model_class._meta.app_label}_{model_class._meta.model_name}"
    ).first()
    assert fs
    assert fs.fields.exists()
