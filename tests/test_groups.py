import pytest
from testutils.factories import FieldDefinitionFactory, FieldsetFactory

from hope_flex_fields.models import DataChecker, DataCheckerFieldset, FlexField


@pytest.fixture
def setup_data(db):
    field_def = FieldDefinitionFactory()

    documents_fieldset = FieldsetFactory(name="Documents", default_group="documents")
    personal_fieldset = FieldsetFactory(name="Personal", default_group="personal")
    root_fieldset = FieldsetFactory(name="Root", default_group="")

    doc_field = FlexField.objects.create(name="document_name", definition=field_def, fieldset=documents_fieldset)
    personal_field = FlexField.objects.create(name="first_name", definition=field_def, fieldset=personal_fieldset)
    root_field = FlexField.objects.create(name="id", definition=field_def, fieldset=root_fieldset)

    datachecker = DataChecker.objects.create(name="TestChecker")

    return {
        "field_def": field_def,
        "documents_fieldset": documents_fieldset,
        "personal_fieldset": personal_fieldset,
        "root_fieldset": root_fieldset,
        "doc_field": doc_field,
        "personal_field": personal_field,
        "root_field": root_field,
        "datachecker": datachecker,
    }


def test_fieldset_default_group(setup_data):
    documents_fieldset = setup_data["documents_fieldset"]
    personal_fieldset = setup_data["personal_fieldset"]
    root_fieldset = setup_data["root_fieldset"]

    assert documents_fieldset.default_group == "documents"
    assert personal_fieldset.default_group == "personal"
    assert root_fieldset.default_group == ""


def test_datachecker_fieldset_override_fields(setup_data):
    datachecker = setup_data["datachecker"]
    documents_fieldset = setup_data["documents_fieldset"]

    dc_fieldset = DataCheckerFieldset.objects.create(
        checker=datachecker,
        fieldset=documents_fieldset,
        override_default_value=True,
        override_group="custom_docs",
    )

    assert dc_fieldset.override_default_value is True
    assert dc_fieldset.override_group == "custom_docs"


def test_get_fields_with_groups_no_override(setup_data):
    datachecker = setup_data["datachecker"]
    documents_fieldset = setup_data["documents_fieldset"]

    DataCheckerFieldset.objects.create(checker=datachecker, fieldset=documents_fieldset, override_default_value=False)

    fields_with_groups = list(datachecker.get_fields_with_groups())
    assert len(fields_with_groups) == 1

    fs, field, group = fields_with_groups[0]
    assert group == "documents"  # Should use fieldset's default_group


def test_get_fields_with_groups_with_override(setup_data):
    datachecker = setup_data["datachecker"]
    documents_fieldset = setup_data["documents_fieldset"]

    DataCheckerFieldset.objects.create(
        checker=datachecker,
        fieldset=documents_fieldset,
        override_default_value=True,
        override_group="custom_group",
    )

    fields_with_groups = list(datachecker.get_fields_with_groups())
    assert len(fields_with_groups) == 1

    fs, field, group = fields_with_groups[0]
    assert group == "custom_group"  # Should use override_group


def test_get_fields_with_groups_override_empty(setup_data):
    datachecker = setup_data["datachecker"]
    documents_fieldset = setup_data["documents_fieldset"]

    DataCheckerFieldset.objects.create(
        checker=datachecker, fieldset=documents_fieldset, override_default_value=True, override_group=""
    )

    fields_with_groups = list(datachecker.get_fields_with_groups())
    assert len(fields_with_groups) == 1

    fs, field, group = fields_with_groups[0]
    assert group == ""  # Should be empty string when override_group is empty


def test_get_fields_with_groups_multiple_fieldsets(setup_data):
    datachecker = setup_data["datachecker"]
    documents_fieldset = setup_data["documents_fieldset"]
    personal_fieldset = setup_data["personal_fieldset"]
    root_fieldset = setup_data["root_fieldset"]

    DataCheckerFieldset.objects.create(checker=datachecker, fieldset=documents_fieldset, override_default_value=False)
    DataCheckerFieldset.objects.create(
        checker=datachecker,
        fieldset=personal_fieldset,
        override_default_value=True,
        override_group="custom_personal",
    )
    DataCheckerFieldset.objects.create(checker=datachecker, fieldset=root_fieldset, override_default_value=False)

    fields_with_groups = list(datachecker.get_fields_with_groups())
    assert len(fields_with_groups) == 3

    groups = [group for _, _, group in fields_with_groups]
    assert "documents" in groups
    assert "custom_personal" in groups
    assert "" in groups  # root fieldset has empty group


def test_get_fields_method(setup_data):
    datachecker = setup_data["datachecker"]
    documents_fieldset = setup_data["documents_fieldset"]

    DataCheckerFieldset.objects.create(checker=datachecker, fieldset=documents_fieldset, override_default_value=False)

    fields = list(datachecker.get_fields())
    assert len(fields) == 1

    fs, field = fields[0]
    assert field.name == "document_name"
    assert fs.fieldset == documents_fieldset


def test_get_field_method(setup_data):
    datachecker = setup_data["datachecker"]
    documents_fieldset = setup_data["documents_fieldset"]

    DataCheckerFieldset.objects.create(checker=datachecker, fieldset=documents_fieldset, override_default_value=False)

    field = datachecker.get_field("document_name")
    assert field is not None
    assert field.name == "document_name"

    field = datachecker.get_field("non_existent")
    assert field is None
