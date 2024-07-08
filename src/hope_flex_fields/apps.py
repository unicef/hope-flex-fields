from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_fields(sender, **kwargs):
    from hope_flex_fields.models import FieldDefinition
    from hope_flex_fields.registry import field_registry

    for fld in field_registry:
        FieldDefinition.objects.get_from_django_field(fld)


class Config(AppConfig):
    name = "hope_flex_fields"
    verbose_name = "Flex Fields"

    def ready(self):
        post_migrate.connect(create_default_fields, sender=self)
