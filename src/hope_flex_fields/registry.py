from django import forms

from strategy_field.registry import Registry
from strategy_field.utils import fqn, import_by_name


class FieldRegistry(Registry):
    def get_name(self, entry):
        return entry.__name__

    def cast(self, item: str) -> type:
        if item in self:
            if isinstance(item, str):
                try:
                    clazz = import_by_name(item)
                except (ImportError, ValueError):
                    raise KeyError(item)
            else:
                clazz = item
        return clazz

    def __getitem__(self, item):
        return super().__getitem__(item)

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
