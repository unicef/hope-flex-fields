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
    fd_int = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fd_float = FieldDefinitionFactory(field_type=forms.FloatField, attrs={"min_value": 1})
    fd_text = FieldDefinitionFactory(field_type=forms.CharField, attrs={"required": False})

    fs = FieldsetFactory()
    FlexFieldFactory(name="int", definition=fd_int, fieldset=fs, attrs={})
    FlexFieldFactory(name="float", definition=fd_float, fieldset=fs, attrs={"required": True})
    FlexFieldFactory(name="document_number", definition=fd_text, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="country", definition=fd_text, fieldset=fs, attrs={"required": False})
    return fs


@pytest.fixture
def record2(db):
    ct = ContentType.objects.get_for_model(User)
    return Fieldset.objects.create_from_content_type("Test", ct)


def test_detect_changes(app, record2):
    url = reverse("admin:hope_flex_fields_fieldset_detect_changes", args=[record2.pk])
    app.get(url)


def test_fieldset_test(app, record):
    record.validation = """
        return data.document_number && !data.country
        ? ({ country: "country is required when document number is provided." })
        : true;
        """.strip()
    record.save(update_fields=["validation"])

    url = reverse("admin:hope_flex_fields_fieldset_test", args=[record.pk])
    res = app.get(url)

    def submit(**data):
        form = res.forms["test"]
        for k, v in data.items():
            form[k] = v
        return form.submit()

    res = submit(int="1")
    assert [m.message for m in res.context["messages"]] == ["Please correct the errors below"]

    res = submit(int="1", float="1.1", document_number="", country="")
    assert [m.message for m in res.context["messages"]] == ["Valid"]

    res = submit(int="1", float="1.1", document_number="ABC", country="")
    assert [m.message for m in res.context["messages"]] == ["Please correct the errors below"]
    assert b"country is required when document number is provided." in res.content

    res = submit(int="1", float="1.1", document_number="ABC", country="CL")
    assert [m.message for m in res.context["messages"]] == ["Valid"]


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


def test_all_fields_method_inlineformset_factory(app, record):
    url = reverse("admin:hope_flex_fields_fieldset_all_fields", args=[record.pk])

    res = app.get(url)
    assert res.status_code == 200
    assert "formset" in res.context


def test_all_fields_duplicate_name_validation(app, record):
    url = reverse("admin:hope_flex_fields_fieldset_all_fields", args=[record.pk])

    res = app.get(url)
    assert res.status_code == 200

    form = None
    for f in res.forms.values():
        if "fields-INITIAL_FORMS" in f.fields:
            form = f
            break

    assert form is not None
    initial_forms = int(form["fields-INITIAL_FORMS"].value)
    new_form_idx = initial_forms
    form[f"fields-{new_form_idx}-name"] = "int"

    res = form.submit()

    assert res.status_code == 200
    assert b"Field with this name already exists in the fieldset." in res.content
