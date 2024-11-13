from abc import ABC, abstractmethod
from typing import Any


class ChildFieldMixin(ABC):

    @abstractmethod
    def validate_with_parent(self, parent_value: Any, value: Any) -> None: ...

    @abstractmethod
    def get_choices_for_parent_value(self, parent_value: Any, only_codes=False) -> list[tuple[str, str]]: ...
    def validate(self, value): ...
