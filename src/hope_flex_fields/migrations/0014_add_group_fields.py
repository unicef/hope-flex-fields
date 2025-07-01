# Generated manually for adding group fields

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hope_flex_fields", "0013_fielddefinition_validated_alter_datachecker_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="fieldset",
            name="default_group",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name="datacheckerfieldset",
            name="override_group",
            field=models.CharField(default="root", max_length=32),
        ),
        migrations.AddField(
            model_name="datacheckerfieldset",
            name="override_default_value",
            field=models.BooleanField(default=False),
        ),
    ]
