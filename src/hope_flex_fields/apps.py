from django.apps import AppConfig
from django.db.models.signals import post_migrate

from strategy_field.utils import fqn


def create_default_fields(sender, **kwargs):
    from hope_flex_fields.models import FieldDefinition
    from hope_flex_fields.registry import field_registry
    from hope_flex_fields.utils import get_kwargs_for_field

    for fld in field_registry:
        FieldDefinition.objects.get_or_create(
            name=fld.__name__,
            field_type=fqn(fld),
            defaults={"attrs": get_kwargs_for_field(fld)},
        )


class Config(AppConfig):
    name = "hope_flex_fields"
    verbose_name = "Flex Fields"

    def ready(self):
        post_migrate.connect(create_default_fields, sender=self)
