from unittest import mock

from django import forms

import pytest
from testutils.factories import FlexFieldFactory

from hope_flex_fields.xlsx import get_validation_for_field


@pytest.mark.parametrize(
    "ft", [forms.ChoiceField, forms.IntegerField, forms.BooleanField, forms.DateField]
)
def test_get_validation_for_field(db, ft):
    f = FlexFieldFactory(field__field_type=ft, field__attrs={}, attrs={})
    with mock.patch.object(f, "attrs", {}):
        with mock.patch.object(f.field, "attrs", {}):
            get_validation_for_field(f)
