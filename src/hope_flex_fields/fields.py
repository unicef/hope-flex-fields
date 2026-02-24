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
    - During validation, values are automatically checked for uniqueness
      across the dataset (duplicate values produce a validation error).
    """
