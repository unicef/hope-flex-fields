# Generated migration to add IdentityField to the default FieldDefinition catalogue.
# create_default_fields uses get_or_create so running it again is safe and idempotent.

from django.db import migrations

from hope_flex_fields.utils import create_default_fields


class Migration(migrations.Migration):
    dependencies = [
        (
            "hope_flex_fields",
            "0016_fieldset_validation",
        ),
    ]

    operations = [
        migrations.RunPython(create_default_fields, migrations.RunPython.noop),
    ]
