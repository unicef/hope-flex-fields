from django import forms

import pytest

from hope_flex_fields.models import FieldDefinition, Fieldset


@pytest.mark.example
def test_example_master_detail_data(db):
    COUNTRIES = [{"id": 1, "name": "Italy"}, {"id": 2, "name": "France"}]
    CITIES = [{"country": 1, "name": "Rome"}, {"country": 2, "name": "Paris"}, {"country": 3, "name": "Berlin"}]

    num = FieldDefinition.objects.create(name="Int", field_type=forms.IntegerField)
    char = FieldDefinition.objects.create(name="Char", field_type=forms.CharField)

    country = Fieldset.objects.create(name="Country")
    country.fields.create(name="id", field=num)
    country.fields.create(name="name", field=char)

    city = Fieldset.objects.create(name="City")
    city.fields.create(name="country", field=num)
    city.fields.create(name="name", field=char)

    country.set_primary_key_col("id")
    city.set_master(country, "country")

    if not (errors := country.validate(COUNTRIES)):
        errors = city.validate(CITIES)

    assert errors == {3: {"-": ["'3' not found in master"]}}
