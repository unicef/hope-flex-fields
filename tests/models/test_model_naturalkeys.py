import pytest
from testutils.factories import get_factory_for_model

from hope_flex_fields.models import DataChecker, FieldDefinition, Fieldset, FlexField


@pytest.mark.parametrize("m", [FieldDefinition, Fieldset, FlexField, DataChecker])
def test_natural_keys(db, m):
    f = get_factory_for_model(m)
    r = f()
    assert m.objects.get_by_natural_key(*r.natural_key()) == r
