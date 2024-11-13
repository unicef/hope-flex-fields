from unittest import mock

from django import forms

import pytest
from testutils.factories import FlexFieldFactory

from hope_flex_fields.xlsx import get_validation_for_field


@pytest.mark.parametrize("ft", [forms.ChoiceField, forms.IntegerField, forms.BooleanField, forms.DateField])
def test_get_validation_for_field(db, ft):
    f = FlexFieldFactory(definition__field_type=ft, definition__attrs={}, attrs={})
    with mock.patch.object(f, "attrs", {}):
        with mock.patch.object(f.definition, "attrs", {}):
            get_validation_for_field(f)
