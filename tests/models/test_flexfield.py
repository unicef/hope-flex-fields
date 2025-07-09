from django import forms
from django.core.exceptions import ValidationError
from unittest.mock import patch

import pytest


def test_validate_attrs_with_exception(db):
    from hope_flex_fields.models import FieldDefinition, FlexField

    fd = FieldDefinition(name="ExceptionField", field_type=forms.IntegerField, attrs={"invalid_attr": "invalid_value"})
    flexfield = FlexField(definition=fd, name="exception_field", fieldset_id=1)

    with patch.object(flexfield, "get_field", side_effect=Exception("Field creation error")):
        with pytest.raises(ValidationError) as exc_info:
            flexfield.validate_attrs()
        assert "Field creation error" in str(exc_info.value)


def test_get_field_with_exception(db):
    from hope_flex_fields.models import FieldDefinition, FlexField
    from hope_flex_fields.exceptions import FlexFieldCreationError

    fd = FieldDefinition(name="ExceptionField", field_type=forms.IntegerField, attrs={"invalid_attr": "invalid_value"})
    flexfield = FlexField(definition=fd, name="exception_field", fieldset_id=1)

    with patch("hope_flex_fields.models.flexfield.type", side_effect=Exception("Type creation error")):
        with pytest.raises(FlexFieldCreationError) as exc_info:
            flexfield.get_field()
        assert "Error creating field for FlexField exception_field" in str(exc_info.value)
