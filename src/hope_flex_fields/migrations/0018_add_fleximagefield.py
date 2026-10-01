# Points the FlexImageField definition at the library implementation of the field.
#
# A project that shipped its own FlexImageField before it moved here already has a
# definition under that name, and FieldDefinition.name is unique, so the existing row
# is repointed instead of a second one being created. The update goes through the
# queryset so that the old field_type is never deserialized, which would fail as soon
# as the project drops its own class.

from django.db import migrations
from django.utils.text import slugify

from strategy_field.utils import fqn

from hope_flex_fields.fields import FlexImageField
from hope_flex_fields.utils import get_common_attrs, get_kwargs_from_field_class


def add_flex_image_field(apps, schema_editor):
    field_definition = apps.get_model("hope_flex_fields", "FieldDefinition")
    name = FlexImageField.__name__
    existing = field_definition.objects.filter(name=name)
    if existing.exists():
        existing.update(field_type=fqn(FlexImageField))
        return
    field_definition.objects.create(
        name=name,
        slug=slugify(name),
        field_type=fqn(FlexImageField),
        attrs=get_kwargs_from_field_class(FlexImageField, get_common_attrs()),
    )


class Migration(migrations.Migration):
    dependencies = [
        (
            "hope_flex_fields",
            "0017_add_identityfield",
        ),
    ]

    operations = [
        migrations.RunPython(add_flex_image_field, migrations.RunPython.noop),
    ]
