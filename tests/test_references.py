import logging
from unittest.mock import patch
from uuid import UUID

import pytest

from hope_flex_fields.config import CONFIG
from hope_flex_fields.references import (
    flex_file_src,
    format_reference,
    is_data_uri,
    is_reference,
    parse_reference,
)

FILE_ID = UUID("1b4e28ba-2fa1-11d2-883f-0016d3cca427")
REFERENCE = "flexfile:1b4e28ba-2fa1-11d2-883f-0016d3cca427"
DATA_URI = "data:image/png;base64,iVBORw0KGgo="


@pytest.fixture
def configured_route():
    """Play the part of a project that serves payloads from a named route."""
    with patch.dict(CONFIG, {"FILE_URL_NAME": "flex_file"}):
        yield


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (REFERENCE, True),
        ("flexfile:not-a-uuid", True),
        ("flexfile:", True),
        (DATA_URI, False),
        ("plain value", False),
        ("", False),
        (None, False),
        (FILE_ID, False),
    ],
)
def test_is_reference(value, expected):
    assert is_reference(value) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (DATA_URI, True),
        ("data:", True),
        (REFERENCE, False),
        ("plain value", False),
        ("", False),
        (None, False),
    ],
)
def test_is_data_uri(value, expected):
    assert is_data_uri(value) is expected


@pytest.mark.parametrize("file_id", [FILE_ID, str(FILE_ID)], ids=["uuid", "str"])
def test_format_reference(file_id):
    assert format_reference(file_id) == REFERENCE


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (REFERENCE, FILE_ID),
        ("flexfile:not-a-uuid", None),
        ("flexfile:", None),
        (DATA_URI, None),
        ("plain value", None),
        ("", None),
        (None, None),
    ],
)
def test_parse_reference(value, expected):
    assert parse_reference(value) == expected


def test_format_and_parse_reference_round_trip():
    assert parse_reference(format_reference(FILE_ID)) == FILE_ID


def test_flex_file_src_resolves_reference(configured_route):
    assert flex_file_src(REFERENCE) == "/flex-file/%s/" % FILE_ID


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (DATA_URI, DATA_URI),
        ("flexfile:not-a-uuid", ""),
        ("plain value", ""),
        ("", ""),
        (None, ""),
    ],
)
def test_flex_file_src_passes_through_everything_else(configured_route, value, expected):
    assert flex_file_src(value) == expected


def test_flex_file_src_warns_when_no_route_is_configured(caplog):
    with caplog.at_level(logging.WARNING, logger="hope_flex_fields.references"):
        assert flex_file_src(REFERENCE) == ""
    assert "FILE_URL_NAME" in caplog.text


def test_flex_file_src_warns_when_the_route_does_not_reverse(caplog):
    with patch.dict(CONFIG, {"FILE_URL_NAME": "no-such-route"}):
        with caplog.at_level(logging.WARNING, logger="hope_flex_fields.references"):
            assert flex_file_src(REFERENCE) == ""
    assert "no-such-route" in caplog.text
