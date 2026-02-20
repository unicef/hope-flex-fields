import pytest
from django import forms

from testutils.factories import (
    DataCheckerFactory,
    DataCheckerFieldsetFactory,
    FieldDefinitionFactory,
    FieldsetFactory,
    FlexFieldFactory,
)


@pytest.fixture
def fs(db):
    fd = FieldDefinitionFactory(field_type=forms.CharField, attrs={"required": False})
    fs = FieldsetFactory(validation="return true;")
    for name in ("document_number", "country"):
        FlexFieldFactory(name=name, definition=fd, fieldset=fs)
    return fs


@pytest.mark.parametrize(
    ("prefix", "fmt"),
    [("%s_", "{name}_"), ("member_", "member_{name}")],
    ids=["template_suffix", "concat_prefix"],
)
def test_datachecker_fieldset_specs_map_matches_form_field_names(fs, prefix: str, fmt: str):
    dc = DataCheckerFactory()
    DataCheckerFieldsetFactory(checker=dc, fieldset=fs, prefix=prefix, order=0)

    form_class = dc.get_form_class()
    ((_, bare_to_prefixed),) = form_class.fieldset_specs

    names = [f.name for f in fs.get_fields()]
    expected = {name: fmt.format(name=name) for name in names}

    assert bare_to_prefixed == expected
    assert expected["document_number"] in form_class.base_fields
    assert expected["country"] in form_class.base_fields
