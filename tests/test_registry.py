from django import forms

from hope_flex_fields.registry import field_registry


def test_contains():
    assert forms.CharField in field_registry
