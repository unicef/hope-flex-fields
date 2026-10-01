import importlib

from django import forms
from django.apps import apps

import pytest
from strategy_field.utils import fqn

from hope_flex_fields.fields import FlexImageField
from hope_flex_fields.models import FieldDefinition
from hope_flex_fields.registry import field_registry

migration = importlib.import_module("hope_flex_fields.migrations.0018_add_fleximagefield")

NAME = FlexImageField.__name__


class ProjectImageField(forms.ImageField):
    """Stands in for the copy of the field a project defined before it moved here."""


@pytest.fixture
def project_field():
    if ProjectImageField not in field_registry:
        field_registry.register(ProjectImageField)
    return ProjectImageField


def test_migrations_leave_one_definition_pointing_at_the_library_field(db):
    definitions = FieldDefinition.objects.filter(name=NAME)

    assert definitions.count() == 1
    assert definitions.get().field_type is FlexImageField


def test_running_it_again_changes_nothing(db):
    migration.add_flex_image_field(apps, None)

    assert FieldDefinition.objects.filter(name=NAME).count() == 1


def test_it_repoints_the_definition_a_project_already_owns(db, project_field):
    """`FieldDefinition.name` is unique, so the row has to move rather than be duplicated."""
    FieldDefinition.objects.filter(name=NAME).update(field_type=fqn(project_field))

    migration.add_flex_image_field(apps, None)

    definitions = FieldDefinition.objects.filter(name=NAME)
    assert definitions.count() == 1
    assert definitions.get().field_type is FlexImageField


def test_it_creates_the_definition_when_a_project_has_none(db):
    FieldDefinition.objects.filter(name=NAME).delete()

    migration.add_flex_image_field(apps, None)

    definition = FieldDefinition.objects.get(name=NAME)
    assert definition.field_type is FlexImageField
    assert definition.slug == "fleximagefield"
    assert definition.attrs["required"] is False
