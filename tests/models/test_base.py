import pytest
from django import forms

from hope_flex_fields.fields import IdentityField
from hope_flex_fields.models.base import ValidatorMixin


def test_is_duplicate_with_primary_key():
    validator = ValidatorMixin()
    validator.set_primary_key_col("id")

    class MockForm:
        def __init__(self, cleaned_data):
            self.cleaned_data = cleaned_data

    form1 = MockForm({"id": "123"})
    result = validator.is_duplicate(form1)
    assert result is None
    assert "123" in validator.primary_keys

    form2 = MockForm({"id": "123"})
    result = validator.is_duplicate(form2)
    assert result == "123 duplicated"


def test_collected_values_handling():
    validator = ValidatorMixin()
    validator.collect("field1", "field2")

    class MockForm:
        def __init__(self, cleaned_data):
            self.cleaned_data = cleaned_data

    form = MockForm({"field1": "value1", "field2": "value2"})

    for field_name in validator._collected_values:
        validator._collected_values[field_name].append(form.cleaned_data[field_name])

    assert validator.collected("field1") == ["value1"]
    assert validator.collected("field2") == ["value2"]


@pytest.mark.django_db
def test_identity_field_auto_detected_as_pk():
    """validate() discovers an IdentityField in the form and uses it as the PK column."""
    from testutils.factories import FieldDefinitionFactory, FieldsetFactory, FlexFieldFactory

    fd_uid = FieldDefinitionFactory(field_type=IdentityField)
    fd_name = FieldDefinitionFactory(field_type=forms.CharField)
    fs = FieldsetFactory()
    FlexFieldFactory(name="uid", definition=fd_uid, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="name", definition=fd_name, fieldset=fs, attrs={"required": False})

    data = [{"uid": "A1", "name": "Alice"}, {"uid": "A2", "name": "Bob"}]
    errors = fs.validate(data)

    assert errors == {}
    assert fs._primary_key_field_name == "uid"


@pytest.mark.django_db
def test_identity_field_duplicate_detected():
    """validate() reports a duplicate error when two rows share the same IdentityField value."""
    from testutils.factories import FieldDefinitionFactory, FieldsetFactory, FlexFieldFactory

    fd_uid = FieldDefinitionFactory(field_type=IdentityField)
    fd_name = FieldDefinitionFactory(field_type=forms.CharField)
    fs = FieldsetFactory()
    FlexFieldFactory(name="uid", definition=fd_uid, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="name", definition=fd_name, fieldset=fs, attrs={"required": False})

    data = [{"uid": "X1", "name": "Alice"}, {"uid": "X1", "name": "Bob"}]
    errors = fs.validate(data)

    assert 2 in errors
    assert errors[2]["-"] == ["X1 duplicated"]


@pytest.mark.django_db
def test_explicit_pk_not_overridden_by_identity_field():
    """set_primary_key_col() takes precedence — IdentityField auto-detection is skipped."""
    from testutils.factories import FieldDefinitionFactory, FieldsetFactory, FlexFieldFactory

    fd_uid = FieldDefinitionFactory(field_type=IdentityField)
    fd_seq = FieldDefinitionFactory(field_type=forms.IntegerField)
    fs = FieldsetFactory()
    FlexFieldFactory(name="uid", definition=fd_uid, fieldset=fs, attrs={"required": False})
    FlexFieldFactory(name="seq", definition=fd_seq, fieldset=fs, attrs={"required": False})

    fs.set_primary_key_col("seq")
    # uid is duplicated but seq is the explicit PK, so no duplicate error
    data = [{"uid": "SAME", "seq": 1}, {"uid": "SAME", "seq": 2}]
    errors = fs.validate(data)

    assert errors == {}
    assert fs._primary_key_field_name == "seq"
