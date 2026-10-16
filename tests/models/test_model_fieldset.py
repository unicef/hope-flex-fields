from typing import TYPE_CHECKING

from django import forms
from django.core.exceptions import ValidationError

import pytest
from testutils.factories import FieldDefinitionFactory, FieldsetFactory, FlexFieldFactory

if TYPE_CHECKING:
    from hope_flex_fields.models import FlexField, Fieldset


@pytest.fixture
def config(db):
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


@pytest.fixture
def fs(config) -> "Fieldset":
    return config["fs"]


def test_validate_row(config):
    data = {"int": 1, "float": 1.1, "str": "string"}
    fs: Fieldset = config["fs"]

    ret = fs.validate(data, include_success=False)
    assert ret == {}


def test_validate_fail(config):
    #  try to validate json formatted data against a FieldSet
    data = {"int": 0, "float": 1.1, "str": "string"}
    fs: Fieldset = config["fs"]
    # with pytest.raises(ValidationError) as e:
    ret = fs.validate(data)

    assert ret == {1: {"int": ["Ensure this value is greater than or equal to 1."]}}


def test_validate_regex(config):
    #  try to validate json formatted data against a FieldSet
    data = {"int": 10, "float": 1.1, "str": "string", "int2": "1"}
    fs: Fieldset = config["fs"]
    ret = fs.validate(data)
    assert ret == {1: {"int2": ["Invalid format. Allowed Regex is '\\d\\d\\d'"]}}
    data = {"int": 10, "float": 1.1, "str": "string", "int2": "111"}
    ret = fs.validate(data)
    assert ret == {}


def test_extends(config):
    fs: Fieldset = config["fs"]
    fs2: Fieldset = FieldsetFactory(extends=fs)

    ii: FlexField = fs2.get_field("int")  # NOTE: we get 'int' from fs2
    assert ii.get_field().min_value == 1

    assert [f.name for f in fs2.get_fields()] == ["int", "float", "int1", "int2"]
    # add new field
    FlexFieldFactory(name="int2.1", fieldset=fs2)
    assert [f.name for f in fs2.get_fields()] == [
        "int",
        "float",
        "int1",
        "int2",
        "int2.1",
    ]

    # override existing field
    FlexFieldFactory(
        name=ii.name,
        definition__field_type=ii.definition.field_type,
        fieldset=fs2,
        attrs={"min_value": 100},
    )
    assert [f.name for f in fs2.get_fields()] == [
        "float",
        "int1",
        "int2",
        "int2.1",
        "int",
    ]
    ii = fs2.get_field("int")
    assert ii.get_field().min_value == 100


def test_cannot_extends_self(config):
    fs: Fieldset = config["fs"]
    fs.extends = fs
    pytest.raises(ValidationError, fs.clean)


MSG_COUNTRY_REQUIRED = "country is required when document number is provided."
VALIDATION_COUNTRY_REQUIRED = f"""
return data.document_number && !data.country
  ? ({{ country: "{MSG_COUNTRY_REQUIRED}" }})
  : true;
""".strip()


@pytest.mark.parametrize(
    ("document_number", "country", "expected"),
    [
        ("", "", {}),
        ("ABC", "", {"country": [MSG_COUNTRY_REQUIRED]}),
        ("ABC", "CL", {}),
    ],
    ids=["no_document_number_ok", "document_number_requires_country", "country_provided_ok"],
)
def test_validate_rules_country_required(fs: "Fieldset", document_number: str, country: str, expected: dict):
    fs.validation = VALIDATION_COUNTRY_REQUIRED
    assert fs.has_validation_rules()

    assert fs.validate_rules({"document_number": document_number, "country": country}) == expected


@pytest.mark.parametrize(
    ("validation_code", "data", "expected"),
    [
        ("return 123;", {"anything": "ok"}, {}),
        ("boom();", {"anything": "ok"}, None),
        ("return true;", {"x": object()}, None),
    ],
    ids=["non_object_return_is_ok", "js_exception_is_non_field_error", "non_serializable_data_is_non_field_error"],
)
def test_validate_rules_engine_failures_are_non_field_errors(
    fs: "Fieldset", validation_code: str, data: dict, expected
):
    fs.validation = validation_code
    ret = fs.validate_rules(data)

    if expected is not None:
        assert ret == expected
    else:
        assert ret["-"]
        assert isinstance(ret.get("-"), list)


@pytest.mark.parametrize(
    ("prefix", "expected_format"),
    [
        ("", "{name}"),
        ("pfx_", "pfx_{name}"),
        ("grp__%s", "grp__{name}"),
        ("A_%s_B", "A_{name}_B"),
    ],
)
def test_get_prefixed_field_map(fs: "Fieldset", prefix: str, expected_format: str):
    names = [f.name for f in fs.get_fields()]
    assert fs.get_prefixed_field_map(prefix) == {n: expected_format.format(name=n) for n in names}


def test_get_validation_errors_maps_prefixed_and_non_field(fs: "Fieldset"):
    fs.validation = VALIDATION_COUNTRY_REQUIRED

    m = {"document_number": "m_document_number", "country": "m_country"}
    assert fs.get_validation_errors({"m_document_number": "ABC", "m_country": ""}, bare_to_prefixed=m) == {
        "m_country": [MSG_COUNTRY_REQUIRED]
    }

    fs.validation = 'return {"-": "General validation failure"};'
    assert fs.get_validation_errors({"x": 1}) == {None: ["General validation failure"]}
