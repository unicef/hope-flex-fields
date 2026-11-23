---
title: File fields
---

A flex field can hold a file rather than text. Because a `Fieldset` is normally
validated against data that ends up serialised as JSON, carrying image bytes
inline makes those records large and slow to read. File-typed fields therefore
store a short **reference** instead, and the payload lives wherever the project
using this library decided to put it.

```
flexfile:1b4e28ba-2fa1-11d2-883f-0016d3cca427
```

The library owns the field type, the reference format, and the API for finding
file fields. It deliberately does **not** own storage: writing the bytes, deciding
who is allowed to read them back, and serving them are the project's job, since
those depend on the project's own models and permissions.

## Declaring a file field

Register a `FieldDefinition` with `FlexImageField` as its field type. Every flex
field built from it renders as a thumbnail with the usual *clear* checkbox, and
reports itself as a file field to the rest of the library.

`FlexImageField.clean()` validates the upload and then returns the reference that
was already on the record, discarding the uploaded file. This is intentional: only
the project's save layer holds both the uploaded file and the record to attach it
to, so it is the only place that can store the payload and produce a new reference.
A `clean()` that returned the file would put bytes into data meant to stay JSON.

!!! note
    Uploads are validated by `django.forms.ImageField`, which relies on
    [Pillow](https://pypi.org/project/pillow/). It is installed as a dependency
    of this library.

## Serving payloads

`flex_file_src()` turns a stored value into something usable as an `<img src>`.
It reverses the route named by `FILE_URL_NAME`, so point that at the view the
project serves payloads from:

```python
FLEX_FIELDS_CONFIG = {
    "FILE_URL_NAME": "myapp:flex_file",
}
```

The route is reversed with the file id as its only argument. When it is not
configured, or does not reverse, `flex_file_src()` returns an empty string and
logs a warning; the widget then shows the raw value as text instead of a broken
image.

Values that are not references pass through unchanged when they are inline
`data:` URIs, so records that predate the move to references keep rendering while
a project migrates them.

## Finding file fields

Consumers usually need to treat file fields differently from the rest: excluding
them from an export template, refusing to bulk-edit them, skipping them in a list
display. Two members cover that, so nobody has to inspect field types by hand:

- [`FlexField.is_file`][hope_flex_fields.models.FlexField.is_file] — whether this
  field holds file data, that is, whether its type derives from `forms.FileField`.
- [`DataChecker.get_file_field_names`][hope_flex_fields.models.DataChecker.get_file_field_names]
  — the names of those fields. Pass `with_prefix=False` for bare names as declared
  on the fieldset; the default returns them prefixed exactly as
  `get_form_class()` names them, so they can be used as keys into cleaned data.
- [`DataChecker.split_data`][hope_flex_fields.models.DataChecker.split_data] —
  splits a mapping into `fields` and `files` using the above.

## Deprecated inline storage

`Base64ImageField` and `Base64ImageInput` are the previous behaviour: they encode
the upload into the record as a `data:` URI. They are kept for one release and are
**not** registered by default, so a project still moving away from them registers
them itself. The deprecated widget inherits the new rendering, which handles both
references and `data:` URIs, so swapping the field type and migrating the stored
data can happen in either order.

## Reference

### ::: hope_flex_fields.references
    options:
        show_root_heading: false
        show_source: true

### ::: hope_flex_fields.fields.FlexImageField
    options:
        show_bases: false
        show_root_heading: true
        show_source: true
