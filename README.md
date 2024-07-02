# HOPR FlexFields

[![Test](https://github.com/unicef/hope-flex-fields/actions/workflows/test.yml/badge.svg)](https://github.com/unicef/hope-flex-fields/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/unicef/hope-flex-fields/graph/badge.svg?token=GSYAH4IEUK)](https://codecov.io/gh/unicef/hope-flex-fields)

## Install
    CSP_SCRIPT_SRC = [
        ...
        "cdnjs.cloudflare.com",
    ]

    INSTALLED_APPS = [
        ...
        'admin_extra_buttons',
        'jsoneditor',
        'hope_flex_fields',
    
    ]

## Demo Application

    python manage.py migrate
    python manage.py runserver

Navigate to http://localhost:8000/admin/ and login using any username/password
