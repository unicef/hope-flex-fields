from django.apps import AppConfig

from strategy_field.utils import fqn


class Config(AppConfig):
    name = "hope_flex_fields"
    verbose_name = "Flex Fields"

    def ready(self):
        from hope_flex_fields.models import FieldDefinition
        from hope_flex_fields.registry import field_registry
        from hope_flex_fields.utils import get_kwargs_for_field

        for fld in field_registry:
            FieldDefinition.objects.get_or_create(
                name=fld.__name__,
                field_type=fqn(fld),
                defaults={"attrs": get_kwargs_for_field(fld)},
            )
