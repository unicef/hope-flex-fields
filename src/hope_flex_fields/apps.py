from django.apps import AppConfig
from django.db.models.signals import post_migrate


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
        post_migrate.connect(sync_content_types, sender=self)
