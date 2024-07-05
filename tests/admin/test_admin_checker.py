from pathlib import Path

from django import forms
from django.urls import reverse

import pytest
from testutils.factories import DataCheckerFactory
from webtest import Upload

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
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs1, prefix="fs1_")
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs2, prefix="fs2_")
    return dc


@pytest.fixture
def dc(db):
    from testutils.factories import (
        DataCheckerFieldsetFactory,
        FieldDefinitionFactory,
        FieldsetFactory,
        FlexFieldFactory,
    )

    fd1 = FieldDefinitionFactory(
        field_type=forms.IntegerField, attrs={"min_value": 1, "max_value": 100}
    )
    fd2 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fd3 = FieldDefinitionFactory(
        field_type=forms.IntegerField, attrs={"max_value": 100}
    )
    fd4 = FieldDefinitionFactory(field_type=forms.FloatField, attrs={})
    fd5 = FieldDefinitionFactory(field_type=forms.DateField, attrs={})
    fd6 = FieldDefinitionFactory(field_type=forms.BooleanField)
    fd7 = FieldDefinitionFactory(
        field_type=forms.ChoiceField,
        attrs={"choices": [["a", "a"], ["b", "b"], ["c", "c"]]},
    )
    fs = FieldsetFactory()
    FlexFieldFactory(name="int1", field=fd1, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="int2", field=fd2, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="int3", field=fd3, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="float", field=fd4, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="date", field=fd5, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="bool", field=fd6, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="choice", field=fd7, fieldset=fs, attrs={"required": False})

    dc = DataCheckerFactory()
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs, prefix="fs")
    return dc


@pytest.fixture
def rdi(db):
    from testutils.factories import (
        DataCheckerFieldsetFactory,
        FieldDefinitionFactory,
        FieldsetFactory,
        FlexFieldFactory,
    )

    cher = FieldDefinitionFactory(field_type=forms.CharField)
    fs = FieldsetFactory()
    FlexFieldFactory(
        name="household_id", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="residence_status_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="consent_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="country_origin_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="country_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="address_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="admin1_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="admin2_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="hh_geopoint_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="unhcr_hh_id_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="returnee_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="size_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="pregnant_member_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="f_0_5_age_group_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="f_6_11_age_group_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="f_12_17_age_group_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="f_adults_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="f_pregnant_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="m_0_5_age_group_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="m_6_11_age_group_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="m_12_17_age_group_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="m_adults_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="f_0_5_disability_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="f_6_11_disability_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="f_12_17_disability_h_c",
        field=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="f_12_17_disability_h_c",
        field=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="f_adults_disability_h_c",
        field=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="m_0_5_disability_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="m_6_11_disability_h_c", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="m_12_17_disability_h_c",
        field=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="m_adults_disability_h_c",
        field=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="unaccompanied_child_h_f",
        field=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="recent_illness_child_h_f",
        field=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="difficulty_breathing_h_f",
        field=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="treatment_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="treatment_facility_h_f",
        field=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="other_treatment_facility_h_f",
        field=cher,
        fieldset=fs,
        attrs={"required": False},
    )
    FlexFieldFactory(
        name="living_situation_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="number_of_rooms_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="total_dwellers_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="one_room_dwellers_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="total_households_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="water_source_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="sufficient_water_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="latrine_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="meals_yesterday_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="food_consumption_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="cereals_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="tubers_roots_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="vegetables_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="fruits_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="meat_fish_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="pulses_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="dairy_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="oilfat_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="sugarsweet_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="condiments_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="assistance_type_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )
    FlexFieldFactory(
        name="assistance_source_h_f", field=cher, fieldset=fs, attrs={"required": False}
    )

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


def test_datachecker_xls_importer(app, dc):
    url = reverse(
        "admin:hope_flex_fields_datachecker_create_xls_importer", args=[dc.pk]
    )
    res = app.get(url)
    assert res.status_code == 200
    # with Path("aaaa.xlsx").open("wb") as f:
    #     f.write(res.body)


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
