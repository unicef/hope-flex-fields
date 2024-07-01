from django import forms
from django.core.exceptions import ObjectDoesNotExist

from strategy_field.exceptions import StrategyAttributeError
from strategy_field.registry import Registry
from strategy_field.utils import fqn, import_by_name


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

    # def __contains__(self, y):
    #     if isinstance(y, str):
    #         return y in [fqn(s) for s in self]
    #     try:
    #         return super().__contains__(y)
    #     except StrategyAttributeError:
    #         return get_custom_field(y)


field_registry = FieldRegistry(forms.Field)
field_registry.register(forms.CharField)
field_registry.register(forms.DateField)
field_registry.register(forms.DecimalField)
field_registry.register(forms.IntegerField)
