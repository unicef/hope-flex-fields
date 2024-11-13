from strategy_field.registry import Registry
from strategy_field.utils import fqn

from .abstract import AbstractAttributeHandler
from .default import DefaultAttributeHandler


class AttributeHandlerRegistry(Registry):
    def get_name(self, entry):
        return entry.__name__

    def as_choices(self):
        if not self._choices:
            self._choices = sorted(
                [(fqn(klass), self.get_name(klass)) for klass in self],
                key=lambda e: e[1],
            )
        return self._choices


attributes_registry = AttributeHandlerRegistry(AbstractAttributeHandler)

attributes_registry.register(DefaultAttributeHandler)
