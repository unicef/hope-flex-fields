from rest_framework.test import APIClient

from testutils.factories import FieldDefinitionFactory


def test_fields(admin_user):
    FieldDefinitionFactory()
    client = APIClient()
    client.force_authenticate(user=admin_user)
    response = client.get('http://testserver/api/fields/')
    assert response.json()
