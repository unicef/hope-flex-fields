from django.contrib.contenttypes.models import ContentType

import pytest
from testutils.factories import ContentTypeFactory, FieldsetFactory, FlexFieldFactory

from hope_flex_fields.apps import sync_content_types
from hope_flex_fields.models import Fieldset


@pytest.fixture
def data(db):
    ct = ContentType.objects.get(app_label="auth", model="user")
    data = Fieldset.objects.inspect_content_type(ct)
    Fieldset.objects.create_from_content_type(name="FS #2", content_type=ct, config=data["config"])


def test_sync_content_types(data):
    fs = FieldsetFactory(content_type=ContentTypeFactory())
    attrs = Fieldset.objects.inspect_content_type(fs.content_type)
    FlexFieldFactory(fieldset=fs, definition__name="CharField", name="username")
    FlexFieldFactory(
        fieldset=fs,
        definition__name="CharField",
        name="password",
        attrs=attrs["config"]["password"],
    )
    FlexFieldFactory(
        fieldset=fs,
        definition__name="CharField",
        name="password",
        attrs=attrs["config"]["password"],
    )
    sync_content_types(None)
