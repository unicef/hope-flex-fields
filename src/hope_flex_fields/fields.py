from typing import TYPE_CHECKING

from django import forms

if TYPE_CHECKING:
    from hope_flex_fields.models import FlexField


class FlexFormMixin(forms.Field):
    flex_field: "FlexField" = None
