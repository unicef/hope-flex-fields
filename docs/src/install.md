---
title: Install
---


## Install

    pip install hope-flex-fields


## Configure

in your `settings.py`


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
