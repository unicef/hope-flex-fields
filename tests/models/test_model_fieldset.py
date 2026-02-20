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


VALIDATION_COUNTRY_REQUIRED = """
return data.document_number && !data.country
  ? ({ country: "country is required when document number is provided." })
  : true;
""".strip()


@pytest.mark.parametrize(
    ("document_number", "country", "expected"),
    [
        ("", "", {}),
        ("ABC", "", {"country": "country is required when document number is provided."}),
        ("ABC", "CL", {}),
    ],
    ids=[
        "no_document_number_ok",
        "document_number_requires_country",
        "country_provided_ok",
    ],
)
def test_validate_rules_country_required(config, document_number: str, country: str, expected: dict):
    fs: Fieldset = config["fs"]
    fs.validation = VALIDATION_COUNTRY_REQUIRED
    fs.save(update_fields=["validation"])

    assert fs.has_validation_rules() is True

    ret = fs.validate_rules({"document_number": document_number, "country": country})
    assert ret == expected


@pytest.mark.parametrize(
    ("validation_code", "data", "expected", "non_field_prefix"),
    [
        (
            "return 123;",
            {"anything": "ok"},
            {"-": ["Validation must return true or an errors object."]},
            None,
        ),
        (
            "boom();",
            {"anything": "ok"},
            None,
            "JavaScript validation error:",
        ),
        (
            "return true;",
            {"x": object()},
            None,
            "Validation data is not JSON-serializable:",
        ),
    ],
    ids=[
        "invalid_return_value_is_non_field_error",
        "js_exception_is_non_field_error",
        "non_serializable_data_is_non_field_error",
    ],
)
def test_validate_rules_engine_failures_are_non_field_errors(
    config,
    validation_code: str,
    data: dict,
    expected: dict | None,
    non_field_prefix: str | None,
):
    fs: Fieldset = config["fs"]
    fs.validation = validation_code
    fs.save(update_fields=["validation"])

    ret = fs.validate_rules(data)

    if expected is not None:
        assert ret == expected
        return

    assert "-" in ret
    assert isinstance(ret["-"], list)
    assert len(ret["-"]) == 1
    assert ret["-"][0].startswith(non_field_prefix or "")


@pytest.mark.parametrize(
    ("prefix", "expected_format"),
    [
        ("", "{name}"),  # Empty prefix -> identity mapping
        ("pfx_", "pfx_{name}"),  # Plain prefix -> concatenation
        ("grp__%s", "grp__{name}"),  # Template prefix with %s -> string formatting
        ("A_%s_B", "A_{name}_B"),  # Template embedded in larger prefix
    ],
)
def test_get_prefixed_field_map(config, prefix, expected_format):
    fs: Fieldset = config["fs"]
    names = [f.name for f in fs.get_fields()]
    expected = {name: expected_format.format(name=name) for name in names}
    assert fs.get_prefixed_field_map(prefix) == expected


def test_get_validation_errors_maps_prefixed_and_non_field(config):
    fs: Fieldset = config["fs"]

    fs.validation = """
    return data.document_number && !data.country
      ? ({ country: "country is required when document number is provided." })
      : true;
    """.strip()
    fs.save(update_fields=["validation"])

    m = {"document_number": "m_document_number", "country": "m_country"}
    assert fs.get_validation_errors({"m_document_number": "ABC", "m_country": ""}, bare_to_prefixed=m) == {
        "m_country": ["country is required when document number is provided."]
    }

    fs.validation = 'return {"-": "General validation failure"};'
    fs.save(update_fields=["validation"])
    assert fs.get_validation_errors({"x": 1}) == {None: ["General validation failure"]}
