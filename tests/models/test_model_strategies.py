from unittest import mock

from django import forms


def test_validate_attributes(db):
    from hope_flex_fields.models import FieldDefinition

    fd = FieldDefinition.objects.create(
        name="IntField", field_type=forms.IntegerField, attrs={}
    )
    fd.refresh_from_db()
    with mock.patch.object(fd.attributes_strategy, "get") as m:
        m.return_value = fd.attrs
        fd.clean()
        assert m.call_count == 1
        assert fd.attributes == {
            "help_text": "",
            "max_value": None,
            "min_value": None,
            "required": False,
            "step_size": None,
        }
        assert m.call_count == 2
