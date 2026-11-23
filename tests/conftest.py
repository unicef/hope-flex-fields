import os
import sys
from pathlib import Path

import pytest
import responses
from django.conf import settings


def pytest_configure(config):
    here = Path(__file__).parent.resolve()
    sys.path.insert(0, str(here / "extra"))
    sys.path.insert(0, str(here / "extra/demoapp"))

    os.environ["DEBUG"] = "0"
    os.environ["ADMINS"] = "admin@demo.org"
    os.environ["CAPTCHA_TEST_MODE"] = "true"
    os.environ["DJANGO_SETTINGS_MODULE"] = "demo.settings"
    import django  # noqa

    django.setup()

    # PBKDF2 is deliberately slow; every UserFactory and test login would pay for it.
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


@pytest.fixture
def app(django_app_factory, mocked_responses):
    from testutils.factories import SuperUserFactory  # noqa

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def fieldset1(django_app_factory, mocked_responses):
    from testutils.factories import FieldsetFactory  # noqa

    FieldsetFactory()
    from testutils.factories import SuperUserFactory  # noqa

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app
