from pathlib import Path

from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse

import pytest
from testutils.factories import DataCheckerFactory
from webtest import Upload

from hope_flex_fields.fields import IdentityField
from hope_flex_fields.models import Fieldset

pytestmark = [pytest.mark.admin, pytest.mark.smoke, pytest.mark.django_db]


@pytest.fixture
def record(db):
    from testutils.factories import (  # noqa
        DataCheckerFieldsetFactory,
        FieldDefinitionFactory,
        FieldsetFactory,
        FlexFieldFactory,
    )

    fd1 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fd2 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fs1 = FieldsetFactory()
    fs2 = FieldsetFactory()
    FlexFieldFactory(name="int1", definition=fd1, fieldset=fs1, attrs={"required": False})
    FlexFieldFactory(name="int2", definition=fd2, fieldset=fs2, attrs={"required": True})

    dc = DataCheckerFactory()
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs1, prefix="fs1_%s")
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs2, prefix="fs2_")
    return dc


@pytest.fixture
def dc(db):
    from testutils.factories import (  # noqa
        DataCheckerFieldsetFactory,
        FieldDefinitionFactory,
        FieldsetFactory,
        FlexFieldFactory,
    )

    fd1 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1, "max_value": 100})
    fd2 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fd3 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"max_value": 100})
    fd4 = FieldDefinitionFactory(field_type=forms.FloatField, attrs={})
    fd5 = FieldDefinitionFactory(field_type=forms.DateField, attrs={})
    fd6 = FieldDefinitionFactory(field_type=forms.BooleanField)
    fd7 = FieldDefinitionFactory(
        field_type=forms.ChoiceField,
        attrs={"choices": [["a", "a"], ["b", "b"], ["c", "c"]]},
    )
    fd8 = FieldDefinitionFactory(field_type=forms.ChoiceField, attrs={})

    fs = FieldsetFactory()
    FlexFieldFactory(name="int1", definition=fd1, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="int2", definition=fd2, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="int3", definition=fd3, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="float", definition=fd4, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="date", definition=fd5, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="bool", definition=fd6, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="choice", definition=fd7, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="choice1", definition=fd8, fieldset=fs, attrs={"required": False})

    dc = DataCheckerFactory()
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs, prefix="fs")
    return dc


@pytest.fixture
def rdi(db):  # noqa
    from testutils.factories import (  # noqa
        DataCheckerFieldsetFactory,
        FieldDefinitionFactory,
        FieldsetFactory,
        FlexFieldFactory,
    )

    cher = FieldDefinitionFactory(field_type=forms.CharField)
    fs = FieldsetFactory()
    FlexFieldFactory(name="household_id", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="residence_status_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="consent_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="country_origin_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="country_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="address_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="admin1_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="admin2_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="hh_geopoint_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="unhcr_hh_id_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="returnee_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="size_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="pregnant_member_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="f_0_5_age_group_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="f_6_11_age_group_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="f_12_17_age_group_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="f_adults_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="f_pregnant_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="m_0_5_age_group_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="m_6_11_age_group_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="m_12_17_age_group_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="m_adults_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="f_0_5_disability_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="f_6_11_disability_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(
        name="f_12_17_disability_h_c",
        definition=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="f_12_17_disability_h_c",
        definition=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="f_adults_disability_h_c",
        definition=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(name="m_0_5_disability_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="m_6_11_disability_h_c", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(
        name="m_12_17_disability_h_c",
        definition=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="m_adults_disability_h_c",
        definition=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="unaccompanied_child_h_f",
        definition=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="recent_illness_child_h_f",
        definition=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="difficulty_breathing_h_f",
        definition=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(name="treatment_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(
        name="treatment_facility_h_f",
        definition=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="other_treatment_facility_h_f",
        definition=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(name="living_situation_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="number_of_rooms_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="total_dwellers_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="one_room_dwellers_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="total_households_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="water_source_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="sufficient_water_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="latrine_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="meals_yesterday_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="food_consumption_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="cereals_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="tubers_roots_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="vegetables_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="fruits_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="meat_fish_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="pulses_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="dairy_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="oilfat_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="sugarsweet_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="condiments_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="assistance_type_h_f", definition=cher, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="assistance_source_h_f", definition=cher, fieldset=fs, attrs={"required": False})

    dc = DataCheckerFactory()
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs, prefix="")
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


def test_datachecker_unique_field(app, record):
    url = reverse("admin:hope_flex_fields_datachecker_add")
    res = app.get(url)
    res.forms["datachecker_form"]["name"] = "DC #1"
    res.forms["datachecker_form"]["members-0-fieldset"] = Fieldset.objects.first().pk
    res.forms["datachecker_form"]["members-0-prefix"] = "pr_"
    res.forms["datachecker_form"]["members-1-fieldset"] = Fieldset.objects.first().pk
    res.forms["datachecker_form"]["members-1-prefix"] = "pr_%s"
    res = res.forms["datachecker_form"].submit()
    assert res.status_code == 200
    assert b"Field names are not unique" in res.content


def test_datachecker_xls_importer(app, dc):
    url = reverse("admin:hope_flex_fields_datachecker_create_xls_importer", args=[dc.pk])
    res = app.get(url)
    assert res.status_code == 200


def test_datachecker_validate_unsupported(app, rdi):
    url = reverse("admin:hope_flex_fields_datachecker_validate", args=[rdi.pk])
    res = app.get(url)
    res.forms["validate-form"]["file"] = Upload("rdi.doc", b"aaa")
    res = res.forms["validate-form"].submit()
    assert res.status_code == 200


def test_datachecker_validate_xls(app, rdi):
    url = reverse("admin:hope_flex_fields_datachecker_validate", args=[rdi.pk])
    data = (Path(__file__).parent / "rdi.xlsx").read_bytes()
    res = app.get(url)
    res.forms["validate-form"]["file"] = Upload("rdi.xlsx", data)
    res = res.forms["validate-form"].submit()
    assert res.status_code == 200


# ── ValidatableFileValidator unit tests ──────────────────────────────────────


def test_validatable_file_validator_accepts_supported_format():
    """No error is raised for a file whose extension is in HANDLERS."""
    from hope_flex_fields.admin.datachecker import ValidatableFileValidator  # noqa

    validator = ValidatableFileValidator()

    class _File:
        name = "data.xlsx"

    validator(_File())  # must not raise


def test_validatable_file_validator_rejects_unsupported_format():
    """ValidationError is raised for a file whose extension is not in HANDLERS."""
    from hope_flex_fields.admin.datachecker import ValidatableFileValidator  # noqa

    validator = ValidatableFileValidator()

    class _File:
        name = "data.csv"

    with pytest.raises(ValidationError):
        validator(_File())


# ── IdentityField enforcement in DataCheckerFieldsetFormset ──────────────────


@pytest.fixture
def two_identity_fieldsets(db):
    """Two fieldsets that each contain one IdentityField flex-field."""
    from testutils.factories import FieldDefinitionFactory, FieldsetFactory, FlexFieldFactory  # noqa

    fd_id = FieldDefinitionFactory(field_type=IdentityField)
    fs1 = FieldsetFactory(name="IDFieldset1")
    fs2 = FieldsetFactory(name="IDFieldset2")
    FlexFieldFactory(name="uid1", definition=fd_id, fieldset=fs1, attrs={"required": False})
    FlexFieldFactory(name="uid2", definition=fd_id, fieldset=fs2, attrs={"required": False})
    return fs1, fs2


def test_datachecker_multiple_identity_fields_rejected(app, two_identity_fieldsets):
    """Saving a DataChecker with two IdentityFields across its fieldsets is rejected."""
    fs1, fs2 = two_identity_fieldsets
    url = reverse("admin:hope_flex_fields_datachecker_add")
    res = app.get(url)
    res.forms["datachecker_form"]["name"] = "DC-MultiID"
    res.forms["datachecker_form"]["members-0-fieldset"] = fs1.pk
    res.forms["datachecker_form"]["members-0-prefix"] = "a_"
    res.forms["datachecker_form"]["members-1-fieldset"] = fs2.pk
    res.forms["datachecker_form"]["members-1-prefix"] = "b_"
    res = res.forms["datachecker_form"].submit()

    assert res.status_code == 200
    assert b"Only one IdentityField is allowed per DataChecker" in res.content


def test_datachecker_single_identity_field_accepted(app, two_identity_fieldsets):
    """Saving a DataChecker with exactly one IdentityField across its fieldsets succeeds."""
    fs1, _fs2 = two_identity_fieldsets
    url = reverse("admin:hope_flex_fields_datachecker_add")
    res = app.get(url)
    res.forms["datachecker_form"]["name"] = "DC-SingleID"
    res.forms["datachecker_form"]["members-0-fieldset"] = fs1.pk
    res.forms["datachecker_form"]["members-0-prefix"] = "a_"
    res = res.forms["datachecker_form"].submit()

    assert res.status_code in (200, 302)


@pytest.fixture
def dc_with_two_identity_members(db):
    """DataChecker that already has two IdentityField members saved via factory
    (bypasses admin formset validation so the conflicting state can exist)."""
    from testutils.factories import (  # noqa
        DataCheckerFactory,
        DataCheckerFieldsetFactory,
        FieldDefinitionFactory,
        FieldsetFactory,
        FlexFieldFactory,
    )

    fd_id = FieldDefinitionFactory(field_type=IdentityField)
    fs1 = FieldsetFactory(name="IDSet-A")
    fs2 = FieldsetFactory(name="IDSet-B")
    FlexFieldFactory(name="uid_a", definition=fd_id, fieldset=fs1, attrs={"required": False})
    FlexFieldFactory(name="uid_b", definition=fd_id, fieldset=fs2, attrs={"required": False})

    dc = DataCheckerFactory()
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs1, prefix="a_")
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs2, prefix="b_")
    return dc


def test_datachecker_deleted_inline_skips_identity_check(app, dc_with_two_identity_members):
    """A formset row marked for DELETE is skipped by DataCheckerFieldsetFormset.clean().

    Without the ``continue`` the two IdentityField members would trigger the
    'Only one IdentityField is allowed' error even though one is being removed.
    """
    dc = dc_with_two_identity_members
    url = reverse("admin:hope_flex_fields_datachecker_change", args=[dc.pk])
    res = app.get(url)
    # Mark the first existing member for deletion — clean() must skip it.
    res.forms["datachecker_form"]["members-0-DELETE"] = True
    res = res.forms["datachecker_form"].submit()

    assert b"Only one IdentityField is allowed per DataChecker" not in res.content
    assert res.status_code in (200, 302)
