"""Parsing and formatting of the ``flexfile:`` reference scheme.

A file-typed flex field does not keep its payload inline: the stored value is a
``flexfile:<uuid>`` reference, and the bytes live wherever the consuming project
decided to put them. Storage and access control are therefore out of scope here.
This module owns the reference format alone, so that every consumer reads and
writes it the same way.
"""

import logging
from typing import Any
from uuid import UUID

from django.urls import NoReverseMatch, reverse

logger = logging.getLogger(__name__)

REFERENCE_PREFIX = "flexfile:"
DATA_URI_FORMAT = "data:{mimetype};base64,{content}"
DATA_URI_PREFIX = "data:"
DEFAULT_MIMETYPE = "application/octet-stream"


def is_reference(value: Any) -> bool:
    """Whether ``value`` is a ``flexfile:`` reference, well formed or not."""
    return isinstance(value, str) and value.startswith(REFERENCE_PREFIX)


def is_data_uri(value: Any) -> bool:
    """Whether ``value`` is an inline ``data:`` URI, the pre-offload storage format."""
    return isinstance(value, str) and value.startswith(DATA_URI_PREFIX)


def format_reference(file_id: UUID | str) -> str:
    """Build the reference to store in place of the payload of ``file_id``."""
    return f"{REFERENCE_PREFIX}{file_id}"


def parse_reference(value: Any) -> UUID | None:
    """Return the file id ``value`` points to, or ``None`` when it points nowhere.

    A malformed reference is not an error: values reach this function from user
    data and from records written before the offload, so callers get ``None``
    and decide how to render the field.
    """
    if not is_reference(value):
        return None
    try:
        return UUID(value.removeprefix(REFERENCE_PREFIX))
    except ValueError:
        return None


def flex_file_src(value: Any) -> str:
    """Return something usable as an ``<img src>``, or ``""`` when nothing can be shown.

    References resolve through the route named by ``FILE_URL_NAME``, which the
    consuming project serves payloads from. Inline ``data:`` URIs pass through
    untouched, so that migrated and not-yet-migrated records render alike.
    """
    if (file_id := parse_reference(value)) is not None:
        return _reverse_file_url(file_id)
    if is_data_uri(value):
        return value
    return ""


def _reverse_file_url(file_id: UUID) -> str:
    from hope_flex_fields.config import CONFIG  # noqa

    url_name = CONFIG["FILE_URL_NAME"]
    if not url_name:
        logger.warning("FLEX_FIELDS_CONFIG['FILE_URL_NAME'] is not set: cannot build an URL for file %s", file_id)
        return ""
    try:
        return reverse(url_name, args=[file_id])
    except NoReverseMatch:
        logger.warning("FLEX_FIELDS_CONFIG['FILE_URL_NAME'] = %r does not reverse with a file id", url_name)
        return ""
