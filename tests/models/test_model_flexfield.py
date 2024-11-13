from django import forms

import pytest


@pytest.fixture
def config(db):
    from testutils.factories import FieldDefinitionFactory, FieldsetFactory, FlexFieldFactory

    fd1 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"min_value": 1})
    fd2 = FieldDefinitionFactory(field_type=forms.FloatField, attrs={"min_value": 1})
    fd3 = FieldDefinitionFactory(field_type=forms.FloatField, attrs={"required": False})
    fd4 = FieldDefinitionFactory(field_type=forms.IntegerField, attrs={"required": False}, regex=r"\d\d\d")

    fs = FieldsetFactory()
    FlexFieldFactory(name="int", definition=fd1, fieldset=fs)
    FlexFieldFactory(name="float", definition=fd2, fieldset=fs)
    FlexFieldFactory(name="int1", definition=fd3, fieldset=fs)
    FlexFieldFactory(name="int2", definition=fd4, fieldset=fs)

    return {"fs": fs}
