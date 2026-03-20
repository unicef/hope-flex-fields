from typing import TYPE_CHECKING

from django import forms

if TYPE_CHECKING:
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
