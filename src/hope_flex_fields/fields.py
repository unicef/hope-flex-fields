from base64 import b64encode
from typing import Literal, TYPE_CHECKING

from django import forms

from hope_flex_fields.references import DATA_URI_FORMAT
from hope_flex_fields.widgets import Base64ImageInput, FlexImageInput

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile

    from hope_flex_fields.models import FlexField


class FlexFormMixin(forms.Field):
    flex_field: "FlexField" = None


class IdentityField(forms.CharField):
    """Marks a record's identity for collision detection.

    Rules enforced by the system:
    - At most one IdentityField may exist per DataChecker.
    - The field is read-only (disabled): its value is set at import time and
      cannot be changed through normal form editing.
    - During import validation, values are automatically checked for uniqueness
      across the dataset (duplicate values produce a validation error).
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("disabled", True)
        super().__init__(*args, **kwargs)


class FlexImageField(forms.ImageField):
    """Image flex field whose value is a reference to an offloaded payload.

    Uploads are validated here but stored elsewhere: only the consuming project
    holds both the uploaded file and the record to attach it to. ``clean`` keeps
    the reference already on the record and leaves it to that project's save
    layer to swap in the new one once the payload has been written.
    """

    widget = FlexImageInput

    def clean(self, data: "UploadedFile | Literal[False] | None", initial: str | None = None) -> str:
        cleaned_data = super().clean(data, initial)
        if not cleaned_data:
            return ""
        if hasattr(cleaned_data, "read"):
            return initial or ""
        return cleaned_data


class Base64ImageField(forms.ImageField):
    """Deprecated: superseded by :class:`FlexImageField`, kept for one release.

    Encodes the upload inline as a ``data:`` URI, which is what records looked
    like before payloads were offloaded. It is not registered by default: a
    project still migrating away from it registers it itself, so that swapping
    the field type and migrating the data can happen in either order.
    """

    widget = Base64ImageInput

    def clean(self, data: "UploadedFile | Literal[False] | None", initial: str | None = None) -> str:
        if cleaned_data := super().clean(data, initial):
            if hasattr(cleaned_data, "read"):
                content = b64encode(cleaned_data.read()).decode()
                return DATA_URI_FORMAT.format(mimetype=data.content_type, content=content)
            return cleaned_data

        return ""
