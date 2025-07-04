import pytest
from django.core.exceptions import ValidationError
from unittest.mock import patch

from hope_flex_fields.attributes.abstract import AbstractAttributeHandler, AttributeHandlerConfig
from testutils.factories import FieldDefinitionFactory

pytestmark = [pytest.mark.django_db]


class ConcreteAttributeHandler(AbstractAttributeHandler):
    def get(self, instance=None):
        return {"test": "value"}

    def set(self, value):
        self.owner.strategy_config = value


def test_config_property_validation_error(db):
    fd = FieldDefinitionFactory(strategy_config={"test": "value"})
    handler = ConcreteAttributeHandler(fd)

    with patch.object(AttributeHandlerConfig, "is_valid", return_value=False):
        with patch.object(AttributeHandlerConfig, "errors", {"field": ["error"]}):
            with pytest.raises(ValidationError) as exc_info:
                _ = handler.config
            assert "field" in str(exc_info.value)
