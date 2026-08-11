import pytest

from django import forms

from hope_flex_fields.registry import field_registry

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


@pytest.fixture
def file_and_text_fieldset(db):
    if forms.FileField not in field_registry:
        field_registry.register(forms.FileField)

    file_def = FieldDefinitionFactory(field_type=forms.FileField, attrs={"required": False})
    text_def = FieldDefinitionFactory(field_type=forms.CharField, attrs={"required": False})
    fs = FieldsetFactory()
    FlexFieldFactory(name="photo", definition=file_def, fieldset=fs)
    FlexFieldFactory(name="full_name", definition=text_def, fieldset=fs)
    return fs


def test_flexfield_is_file_flag(file_and_text_fieldset):
    fields = {f.name: f.is_file for f in file_and_text_fieldset.get_fields()}
    assert fields == {"photo": True, "full_name": False}


@pytest.mark.parametrize(
    ("prefix", "expected"),
    [("", "photo"), ("member_", "member_photo"), ("%s_", "photo_")],
    ids=["no_prefix", "concat_prefix", "template_suffix"],
)
def test_datachecker_get_file_field_names(file_and_text_fieldset, prefix: str, expected: str):
    dc = DataCheckerFactory()
    DataCheckerFieldsetFactory(checker=dc, fieldset=file_and_text_fieldset, prefix=prefix, order=0)

    assert dc.get_file_field_names() == {expected}
    assert dc.get_file_field_names(with_prefix=False) == {"photo"}


def test_datachecker_split_data_separates_files_from_text(file_and_text_fieldset):
    dc = DataCheckerFactory()
    DataCheckerFieldsetFactory(checker=dc, fieldset=file_and_text_fieldset, prefix="", order=0)

    split = dc.split_data({"full_name": "Jane", "photo": "blob", "extra": "x"})

    assert split == {
        "fields": {"full_name": "Jane", "extra": "x"},
        "files": {"photo": "blob"},
    }


def test_datachecker_split_data_uses_provided_file_names(file_and_text_fieldset, mocker):
    dc = DataCheckerFactory()
    DataCheckerFieldsetFactory(checker=dc, fieldset=file_and_text_fieldset, prefix="", order=0)
    get_file_field_names = mocker.patch.object(dc, "get_file_field_names")

    split = dc.split_data(
        {"full_name": "Jane", "photo": "blob", "extra": "x"},
        file_field_names={"photo"},
    )

    get_file_field_names.assert_not_called()
    assert split == {
        "fields": {"full_name": "Jane", "extra": "x"},
        "files": {"photo": "blob"},
    }
