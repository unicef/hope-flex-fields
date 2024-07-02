# Generated by Django 3.2.25 on 2024-07-02 05:23

from django.db import migrations, models
import django.db.models.deletion
import django_regex.fields
import django_regex.validators
import strategy_field.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FieldDefinition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, default='', max_length=500, null=True)),
                ('field_type', strategy_field.fields.StrategyClassField()),
                ('attrs', models.JSONField(blank=True, default={'help_text': '', 'label': None, 'required': False})),
                ('regex', django_regex.fields.RegexField(blank=True, null=True, validators=[django_regex.validators.RegexValidator()])),
                ('validation', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Fieldset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='FieldsetField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('overrides', models.JSONField(blank=True, default=dict)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instances', to='hope_flex_fields.fielddefinition')),
                ('fieldset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='hope_flex_fields.fieldset')),
            ],
            options={
                'unique_together': {('fieldset', 'name')},
            },
        ),
    ]
