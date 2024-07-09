# HOPE FlexFields

[![Test](https://github.com/unicef/hope-flex-fields/actions/workflows/test.yml/badge.svg)](https://github.com/unicef/hope-flex-fields/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/unicef/hope-flex-fields/graph/badge.svg?token=GSYAH4IEUK)](https://codecov.io/gh/unicef/hope-flex-fields)

This library provides the ability to define a set of fields and related validation rules dynamically. It has been designed as part of the [HOPE](https://github.com/unicef/hct-mis) project to manage user-customizable fields (FlexField). The idea is to have a central business logic repository for data import validation.


It provides four classes:

- FieldDefinition: This represents a collection of reusable pre-configured fields
- FlexField: Instance like representation of `FieldDefinition` inside a `Fieldset`
- Fieldset: Group of FlexField
- DataChecker: Compound of fieldset

From the design point of view a high level comparison with Django components could be:

- `FieldDefinition` = `class forms.Field`
- `Fieldset` = `forms.Form`
- `FlexField` = `forms.Field()`
- `DataChecker` = `[forms.Form(),...]`
 
```mermaid 

classDiagram
    class AbstractField
    class FieldDefinition
    class FlexField
    class Fieldset
    class DataChecker
    AbstractField <|-- FlexField
    AbstractField <|-- FieldDefinition
    Fieldset *-- FlexField 
    FlexField --> FieldDefinition
    DataChecker o-- Fieldset

```


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
    python manage.py demo
    python manage.py runserver

Navigate to http://localhost:8000/admin/ and login using any username/password
