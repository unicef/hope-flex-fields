# Generated by Django 5.1.2 on 2024-11-13 18:30

import django.db.models.deletion
import django_regex.fields
import django_regex.validators
import hope_flex_fields.models.base
import hope_flex_fields.utils
import strategy_field.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [
        ("hope_flex_fields", "0001_initial"),
        ("hope_flex_fields", "0002_fieldset_content_type"),
        ("hope_flex_fields", "0003_alter_datachecker_id_alter_datacheckerfieldset_id_and_more"),
        ("hope_flex_fields", "0004_auto_20241009_0643"),
        ("hope_flex_fields", "0005_remove_fielddefinition_unique_name_and_more"),
        ("hope_flex_fields", "0006_alter_datachecker_id_alter_datacheckerfieldset_id_and_more"),
        ("hope_flex_fields", "0007_create_default_fields"),
        ("hope_flex_fields", "0008_fielddefinition_attributes_strategy_and_more"),
        ("hope_flex_fields", "0009_fielddefinition_strategy_config"),
        ("hope_flex_fields", "0010_rename_field_flexfield_definition"),
    ]

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataChecker",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "DataChecker",
                "verbose_name_plural": "DataCheckers",
            },
            bases=(hope_flex_fields.models.base.ValidatorMixin, models.Model),
        ),
        migrations.CreateModel(
            name="DataCheckerFieldset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("prefix", models.CharField(blank=True, default="", max_length=30)),
                ("order", models.PositiveSmallIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="FieldDefinition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, default="", max_length=500, null=True)),
                ("attrs", models.JSONField(blank=True, default=dict)),
                (
                    "regex",
                    django_regex.fields.RegexField(
                        blank=True, null=True, validators=[django_regex.validators.RegexValidator()]
                    ),
                ),
                ("validation", models.TextField(blank=True, default="", null=True)),
                ("field_type", strategy_field.fields.StrategyClassField()),
            ],
            options={
                "verbose_name": "Field Definition",
                "verbose_name_plural": "Field Definitions",
            },
        ),
        migrations.CreateModel(
            name="Fieldset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                (
                    "extends",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hope_flex_fields.fieldset",
                    ),
                ),
            ],
            options={
                "verbose_name": "Fieldset",
                "verbose_name_plural": "Fieldsets",
            },
            bases=(hope_flex_fields.models.base.ValidatorMixin, models.Model),
        ),
        migrations.CreateModel(
            name="FlexField",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_modified", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, default="", max_length=500, null=True)),
                ("attrs", models.JSONField(blank=True, default=dict)),
                (
                    "regex",
                    django_regex.fields.RegexField(
                        blank=True, null=True, validators=[django_regex.validators.RegexValidator()]
                    ),
                ),
                ("validation", models.TextField(blank=True, default="", null=True)),
                (
                    "field",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="instances",
                        to="hope_flex_fields.fielddefinition",
                    ),
                ),
                (
                    "fieldset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fields",
                        to="hope_flex_fields.fieldset",
                    ),
                ),
            ],
            options={
                "verbose_name": "Flex Field",
                "verbose_name_plural": "flex Fields",
            },
        ),
        migrations.AddConstraint(
            model_name="fielddefinition",
            constraint=models.UniqueConstraint(fields=("name",), name="unique_name"),
        ),
        migrations.AddField(
            model_name="datacheckerfieldset",
            name="checker",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="members", to="hope_flex_fields.datachecker"
            ),
        ),
        migrations.AddField(
            model_name="datacheckerfieldset",
            name="fieldset",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="hope_flex_fields.fieldset"),
        ),
        migrations.AddField(
            model_name="datachecker",
            name="fieldsets",
            field=models.ManyToManyField(
                through="hope_flex_fields.DataCheckerFieldset", to="hope_flex_fields.fieldset"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="flexfield",
            unique_together={("fieldset", "name")},
        ),
        migrations.AddField(
            model_name="fieldset",
            name="content_type",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="contenttypes.contenttype"
            ),
        ),
        migrations.AddField(
            model_name="fielddefinition",
            name="content_type",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="contenttypes.contenttype"
            ),
        ),
        migrations.AddField(
            model_name="fielddefinition",
            name="system_data",
            field=models.JSONField(blank=True, default=dict, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name="datachecker",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="datacheckerfieldset",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="fielddefinition",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="fieldset",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="flexfield",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
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
            constraint=models.UniqueConstraint(fields=("name",), name="fielddefinition_unique_name"),
        ),
        migrations.AddConstraint(
            model_name="fielddefinition",
            constraint=models.UniqueConstraint(fields=("slug",), name="fielddefinition_unique_slug"),
        ),
        migrations.AddConstraint(
            model_name="flexfield",
            constraint=models.UniqueConstraint(fields=("name", "fieldset"), name="flexfield_unique_name"),
        ),
        migrations.AddConstraint(
            model_name="flexfield",
            constraint=models.UniqueConstraint(fields=("slug", "fieldset"), name="flexfield_unique_slug"),
        ),
        migrations.AlterField(
            model_name="datachecker",
            name="id",
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="datacheckerfieldset",
            name="id",
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="fielddefinition",
            name="id",
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="fieldset",
            name="id",
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="flexfield",
            name="id",
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.RunPython(
            code=hope_flex_fields.utils.create_default_fields,
        ),
        migrations.AddField(
            model_name="fielddefinition",
            name="attributes_strategy",
            field=strategy_field.fields.StrategyField(
                default="hope_flex_fields.attributes.default.DefaultAttributeHandler",
                help_text="Strategy to use for attributes retrieval",
            ),
        ),
        migrations.AlterField(
            model_name="datachecker",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="datacheckerfieldset",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="fielddefinition",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="fieldset",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="flexfield",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AddField(
            model_name="fielddefinition",
            name="strategy_config",
            field=models.JSONField(blank=True, default=dict, editable=False, null=True),
        ),
        migrations.RenameField(
            model_name="flexfield",
            old_name="field",
            new_name="definition",
        ),
    ]