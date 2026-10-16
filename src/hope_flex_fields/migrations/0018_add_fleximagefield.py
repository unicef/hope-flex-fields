# Points the FlexImageField definition at the library implementation of the field.
#
# A project that shipped its own FlexImageField before it moved here already has a
# definition under that name, and FieldDefinition.name is unique, so the existing row
# is repointed instead of a second one being created. The update goes through the
# queryset so that the old field_type is never deserialized, which would fail as soon
# as the project drops its own class.
#
# The values are fixed rather than derived from the field class, so that later changes
# to the class or to the attribute helpers cannot alter what this migration writes.

from django.db import migrations

FIELD_NAME = "FlexImageField"
FIELD_SLUG = "fleximagefield"
FIELD_TYPE = "hope_flex_fields.fields.FlexImageField"
FIELD_ATTRS = {"required": False, "help_text": "", "max_length": None, "allow_empty_file": False}


def add_flex_image_field(apps, schema_editor):
    field_definition = apps.get_model("hope_flex_fields", "FieldDefinition")
    existing = field_definition.objects.filter(name=FIELD_NAME)
    if existing.exists():
        existing.update(field_type=FIELD_TYPE)
        return
    field_definition.objects.create(
        name=FIELD_NAME,
        slug=FIELD_SLUG,
        field_type=FIELD_TYPE,
        attrs=FIELD_ATTRS,
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
