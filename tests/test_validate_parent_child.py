from typing import Any

from django import forms
from django.core.exceptions import ValidationError

from testutils.factories import FieldDefinitionFactory, FieldsetFactory, FlexFieldFactory

from hope_flex_fields.mixin import ChildFieldMixin
from hope_flex_fields.registry import field_registry
from typing import TYPE_CHECKING

VALID_CHILDS = {"AFG": ["AFG1", "AFG2"]}

if TYPE_CHECKING:
    from hope_flex_fields.models import Fieldset


class Parent(forms.ChoiceField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.choices = (("AFG", "Parent #1"), ("UKR", "Parent #2"))


class Child(ChildFieldMixin, forms.CharField):
    def validate_with_parent(self, parent_value, value):
        childs = VALID_CHILDS.get(parent_value)
        if value and value in childs:
            return
        raise ValidationError("Not valid child for selected parent")

    def validate(self, value):
        pass

    def get_choices_for_parent_value(self, parent_value: Any, only_codes=False) -> list[tuple[str, str]]:
        return []


def test_validate_child(db):
    field_registry.register(Parent)
    field_registry.register(Child)

    fd1 = FieldDefinitionFactory(field_type=Parent)
    fd2 = FieldDefinitionFactory(field_type=Child)

    fs: Fieldset = FieldsetFactory()
    ita = FlexFieldFactory(name="country", definition=fd1, fieldset=fs)
    FlexFieldFactory(name="region", master=ita, definition=fd2, fieldset=fs)

    errors = fs.validate([{"country": "AFG", "region": "AFG1"}])
    assert errors == {}

    errors = fs.validate([{"country": "AFG", "region": "---"}])
    assert errors == {1: {"region": "['Not valid child for selected parent']"}}
