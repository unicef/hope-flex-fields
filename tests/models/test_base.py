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
