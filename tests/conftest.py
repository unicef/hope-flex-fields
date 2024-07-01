import os
import sys
from pathlib import Path

import pytest
import responses


def pytest_configure(config):
    here = Path(__file__).parent.resolve()
    sys.path.insert(0, str(here / "extra"))
    sys.path.insert(0, str(here / "extra/demoapp"))

    os.environ["DEBUG"] = "0"
    os.environ["ADMINS"] = "admin@demo.org"
    os.environ["CAPTCHA_TEST_MODE"] = "true"
    os.environ["DJANGO_SETTINGS_MODULE"] = "demo.settings"
    import django

    django.setup()


@pytest.fixture()
def mocked_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps
