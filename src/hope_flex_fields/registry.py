from django import forms

from strategy_field.registry import Registry
from strategy_field.utils import fqn

# from .fields import OptionField


class FieldRegistry(Registry):
    def get_name(self, entry):
        return entry.__name__

    def as_choices(self):
        if not self._choices:
            self._choices = sorted(
                [(fqn(klass), self.get_name(klass)) for klass in self],
                key=lambda e: e[1],
            )
        return self._choices


field_registry = FieldRegistry(forms.Field)

field_registry.register(forms.BooleanField)
field_registry.register(forms.CharField)
field_registry.register(forms.ChoiceField)
field_registry.register(forms.DateField)
field_registry.register(forms.DateTimeField)
field_registry.register(forms.DecimalField)
field_registry.register(forms.DurationField)
field_registry.register(forms.EmailField)
field_registry.register(forms.FloatField)
field_registry.register(forms.IntegerField)
field_registry.register(forms.MultipleChoiceField)
field_registry.register(forms.RegexField)
field_registry.register(forms.TimeField)
field_registry.register(forms.URLField)
field_registry.register(forms.UUIDField)
field_registry.register(forms.JSONField)
# field_registry.register(OptionField)
