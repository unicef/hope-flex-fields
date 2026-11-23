from base64 import b64decode
from io import BytesIO
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

import pytest
from PIL import Image

from hope_flex_fields.config import CONFIG
from hope_flex_fields.fields import Base64ImageField, FlexImageField
from hope_flex_fields.references import DATA_URI_PREFIX, is_data_uri
from hope_flex_fields.registry import field_registry
from hope_flex_fields.widgets import Base64ImageInput, FlexImageInput

from testutils.factories import FieldDefinitionFactory, FieldsetFactory, FlexFieldFactory

FILE_ID = "1b4e28ba-2fa1-11d2-883f-0016d3cca427"
REFERENCE = "flexfile:%s" % FILE_ID
DATA_URI = "data:image/png;base64,iVBORw0KGgo="


@pytest.fixture
def png():
    buffer = BytesIO()
    Image.new("RGB", (1, 1), "red").save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def upload(png):
    return SimpleUploadedFile("picture.png", png, content_type="image/png")


@pytest.fixture
def configured_route():
    with patch.dict(CONFIG, {"FILE_URL_NAME": "flex_file"}):
        yield


def test_flex_image_field_is_registered():
    assert FlexImageField in field_registry


def test_flex_image_field_reports_itself_as_a_file_field(db):
    definition = FieldDefinitionFactory(field_type=FlexImageField, attrs={"required": False})
    flex_field = FlexFieldFactory(name="picture", definition=definition, fieldset=FieldsetFactory())

    assert flex_field.is_file is True


def test_flex_image_field_keeps_the_existing_reference_on_upload(upload):
    """The payload is written by the project, so `clean` must not lose the old reference."""
    assert FlexImageField(required=False).clean(upload, REFERENCE) == REFERENCE


def test_flex_image_field_returns_empty_when_uploading_without_a_previous_value(upload):
    assert FlexImageField(required=False).clean(upload, None) == ""


def test_flex_image_field_keeps_the_reference_when_nothing_is_uploaded():
    assert FlexImageField(required=False).clean(None, REFERENCE) == REFERENCE


def test_flex_image_field_clears_the_reference(upload):
    """`False` is what `ClearableFileInput` sends when the clear checkbox is ticked."""
    assert FlexImageField(required=False).clean(False, REFERENCE) == ""


def test_flex_image_field_returns_empty_when_there_is_nothing_at_all():
    assert FlexImageField(required=False).clean(None, None) == ""


def test_flex_image_field_still_validates_the_upload():
    not_an_image = SimpleUploadedFile("picture.png", b"nope", content_type="image/png")

    with pytest.raises(ValidationError):
        FlexImageField(required=False).clean(not_an_image, REFERENCE)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("", False), (None, False), (REFERENCE, True), (DATA_URI, True), ("plain value", True)],
)
def test_flex_image_input_treats_any_value_as_initial(value, expected):
    """A reference is a plain string, so the base `url` lookup cannot be used."""
    assert FlexImageInput().is_initial(value) is expected


def test_flex_image_input_previews_a_reference(configured_route):
    html = FlexImageInput().render("picture", REFERENCE, {})

    assert '<img src="/flex-file/%s/"' % FILE_ID in html


def test_flex_image_input_previews_a_legacy_data_uri():
    html = FlexImageInput().render("picture", DATA_URI, {})

    assert '<img src="%s"' % DATA_URI in html


def test_flex_image_input_falls_back_to_the_raw_value(configured_route):
    """An unresolvable value is shown as text rather than as a broken image."""
    html = FlexImageInput().render("picture", "flexfile:not-a-uuid", {})

    assert "<img" not in html
    assert "<em>flexfile:not-a-uuid</em>" in html


def test_flex_image_input_renders_nothing_extra_without_a_value():
    html = FlexImageInput().render("picture", "", {})

    assert "<img" not in html
    assert "<em>" not in html


def test_base64_image_field_encodes_the_upload_inline(upload, png):
    cleaned = Base64ImageField(required=False).clean(upload, None)

    assert cleaned.startswith("%simage/png;base64," % DATA_URI_PREFIX)
    assert b64decode(cleaned.split(",", 1)[1]) == png


def test_base64_image_field_keeps_the_previous_value_when_nothing_is_uploaded():
    assert Base64ImageField(required=False).clean(None, DATA_URI) == DATA_URI


def test_base64_image_field_clears_the_value():
    assert Base64ImageField(required=False).clean(False, DATA_URI) == ""


def test_base64_image_input_renders_like_the_new_widget():
    """The deprecated widget inherits the new rendering, so both orders of migration work."""
    assert isinstance(Base64ImageInput(), FlexImageInput)
    assert is_data_uri(Base64ImageInput().render("picture", DATA_URI, {}).split('src="')[1].split('"')[0])
