# Generated by Django 5.1.2 on 2024-10-09 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("hope_flex_fields", "0004_auto_20241009_0643"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="fielddefinition",
            name="unique_name",
        ),
        migrations.AlterUniqueTogether(
            name="flexfield",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="fielddefinition",
            name="slug",
            field=models.SlugField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="flexfield",
            name="slug",
            field=models.SlugField(blank=True, editable=False, null=True),
        ),
        migrations.AddConstraint(
            model_name="fielddefinition",
            constraint=models.UniqueConstraint(
                fields=("name",), name="fielddefinition_unique_name"
            ),
        ),
        migrations.AddConstraint(
            model_name="fielddefinition",
            constraint=models.UniqueConstraint(
                fields=("slug",), name="fielddefinition_unique_slug"
            ),
        ),
        migrations.AddConstraint(
            model_name="flexfield",
            constraint=models.UniqueConstraint(
                fields=("name", "fieldset"), name="flexfield_unique_name"
            ),
        ),
        migrations.AddConstraint(
            model_name="flexfield",
            constraint=models.UniqueConstraint(
                fields=("slug", "fieldset"), name="flexfield_unique_slug"
            ),
        ),
    ]
