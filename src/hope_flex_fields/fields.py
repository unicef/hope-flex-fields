from typing import TYPE_CHECKING

from django import forms

if TYPE_CHECKING:
    from hope_flex_fields.models import FlexField


class FlexFormMixin(forms.Field):
    flex_field: "FlexField" = None


#
# class OptionField(forms.ChoiceField):
#     def __init__(self, *, endpoint=None, **kwargs):
#         self.endpoint_nane = endpoint
#         self.endpoint = Endpoint.objects.get(name=endpoint)
#         kwargs.pop('choices', None)
#         super().__init__(**kwargs)
