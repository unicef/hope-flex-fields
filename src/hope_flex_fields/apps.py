from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_fields(sender, **kwargs):
    from hope_flex_fields.models import FieldDefinition
    from hope_flex_fields.registry import field_registry

    for fld in field_registry:
        FieldDefinition.objects.get_from_django_field(fld)


def sync_content_types(sender, **kwargs):
    from hope_flex_fields.models import Fieldset

    fs: Fieldset
    changed = {}
    for fs in Fieldset.objects.exclude(content_type__isnull=True):
        current_attrs = Fieldset.objects.inspect_content_type(fs.content_type)
        diff = fs.diff_content_type()
        for field_name, w in diff.items():
            if ff := fs.get_field(field_name):
                changed[field_name] = w
                ff.attrs = current_attrs["config"][field_name]["attrs"]
                ff.save()


class Config(AppConfig):
    name = "hope_flex_fields"
    verbose_name = "Flex Fields"

    def ready(self):
        post_migrate.connect(create_default_fields, sender=self)
        post_migrate.connect(sync_content_types, sender=self)
