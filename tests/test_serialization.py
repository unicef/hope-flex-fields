from typing import TYPE_CHECKING

from django import forms

import pytest
from testutils.factories import DataCheckerFactory

from hope_flex_fields.forms import FlexForm

if TYPE_CHECKING:
    from hope_flex_fields.models import DataChecker, Fieldset


@pytest.fixture
def dc(db):
    from testutils.factories import (
        DataCheckerFieldsetFactory,
        FieldDefinitionFactory,
        FieldsetFactory,
        FlexFieldFactory,
    )

    fd1 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1, "max_value": 100})
    fd5 = FieldDefinitionFactory(field_type=forms.DateField, attrs={})
    fd6 = FieldDefinitionFactory(field_type=forms.BooleanField)
    fd7 = FieldDefinitionFactory(
        field_type=forms.ChoiceField,
        attrs={"choices": [["a", "a"], ["b", "b"], ["c", "c"]]},
    )
    fs: Fieldset = FieldsetFactory()
    FlexFieldFactory(name="int1", definition=fd1, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="date", definition=fd5, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="bool", definition=fd6, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="choice", definition=fd7, fieldset=fs, attrs={"required": False})

    dc = DataCheckerFactory()
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs)
    return dc


def test_serialization(dc: "DataChecker"):
    form_class: "type[FlexForm]" = dc.get_form()
    f = form_class({"int1": "1", "bool": "False", "date": "2024-12-1"})
    assert f.is_valid(), f.errors
    assert f.cleaned_data == {"int1": 1, "bool": False, "date": "2024-12-01", "choice": ""}
