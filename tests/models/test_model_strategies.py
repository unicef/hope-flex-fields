from unittest import mock

from django import forms

from demo.apps import MyHandler
from strategy_field.utils import fqn


def test_validate_attributes(db):
    from hope_flex_fields.models import FieldDefinition

    fd = FieldDefinition.objects.create(name="IntField", field_type=forms.IntegerField, attrs={})
    fd.refresh_from_db()
    with mock.patch.object(fd.attributes_strategy, "get") as m_get:
        with mock.patch.object(fd.attributes_strategy, "set") as m_set:
            m_get.return_value = fd.attrs
            fd.clean()
            assert m_get.call_count == 1
            assert fd.attributes == {
                "help_text": "",
                "max_value": None,
                "min_value": None,
                "required": False,
                "step_size": None,
            }
            assert m_get.call_count == 2
            assert m_set.call_count == 0


def test_validate_custom_strategy(db, mocked_responses):
    from hope_flex_fields.models import FieldDefinition

    mocked_responses.add(
        mocked_responses.GET,
        "http://test.org/data/",
        json={"choices": ["a", "b", "c"]},
    )
    fd = FieldDefinition.objects.create(
        name="IntField",
        field_type=forms.ChoiceField,
        attrs={},
        attributes_strategy=fqn(MyHandler),
        strategy_config={},
    )
    with mock.patch.object(fd.attributes_strategy, "get", wraps=fd.attributes_strategy.get):
        assert fd.attributes == {
            "choices": [("a", "a"), ("b", "b"), ("c", "c")],
            "help_text": "",
            "required": False,
        }
