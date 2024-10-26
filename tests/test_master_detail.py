# mypy: disable-error-code="no-untyped-def"
from typing import Any

from django import forms

import pytest
from testutils.factories import DataCheckerFactory, FieldsetFactory, FlexFieldFactory

from hope_flex_fields.models import Fieldset

MASTER = [{"id": 1, "name": "Italy"}, {"id": 2, "name": "France"}, {"id": 3, "name": "Germany"}]
DETAILS = [{"country_id": 1, "name": "Rome"}, {"country_id": 2, "name": "Paris"}, {"country_id": 3, "name": "Berlin"}]


@pytest.fixture()
def country_validator(db: Any) -> Fieldset:
    fs = FieldsetFactory(name="Country")
    FlexFieldFactory(name="id", fieldset=fs, field__field_type=forms.IntegerField)
    FlexFieldFactory(name="name", fieldset=fs, field__field_type=forms.CharField)
    return fs


@pytest.fixture()
def city_validator(db: Any) -> Fieldset:
    fs = FieldsetFactory()
    FlexFieldFactory(name="country_id", fieldset=fs, field__field_type=forms.IntegerField)
    FlexFieldFactory(name="name", fieldset=fs, field__field_type=forms.CharField)
    return fs


@pytest.fixture()
def checker(city_validator, country_validator) -> Fieldset:
    dc = DataCheckerFactory()
    dc.fieldsets.add(city_validator)
    dc.fieldsets.add(country_validator)
    return dc


def test_validate_multi(country_validator, city_validator) -> None:
    errors1 = country_validator.validate(MASTER)
    errors2 = city_validator.validate(DETAILS)
    assert errors1 == {}
    assert errors2 == {}


def test_validate_master_detail(country_validator, city_validator) -> None:
    country_validator.set_primary_key_col("id")
    city_validator.set_master(country_validator, "country_id")

    errors1 = country_validator.validate(MASTER)
    errors2 = city_validator.validate(DETAILS)
    assert errors1 == {}
    assert errors2 == {}


def test_validate_missing_master(country_validator, city_validator) -> None:
    country_validator.set_primary_key_col("id")
    city_validator.set_master(country_validator, "country_id")
    DETAILS.append({"country_id": 99, "name": "Alien"})

    errors1 = country_validator.validate(MASTER)
    errors2 = city_validator.validate(DETAILS)

    assert errors1 == {}
    assert errors2 == {4: {"-": ["'99' not found in master"]}}
