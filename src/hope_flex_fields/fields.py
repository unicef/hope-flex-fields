from django import forms


class FlexFormMixin(forms.Field):
    pass


#
# class OptionField(forms.ChoiceField):
#     def __init__(self, *, endpoint=None, **kwargs):
#         self.endpoint_nane = endpoint
#         self.endpoint = Endpoint.objects.get(name=endpoint)
#         kwargs.pop('choices', None)
#         super().__init__(**kwargs)
