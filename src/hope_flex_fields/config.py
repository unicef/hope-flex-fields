from django.conf import settings
from django.utils.module_loading import import_string

CONFIG = {
    "API_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "API_AUTHENTICATION_CLASSES": ["rest_framework.authentication.BasicAuthentication"],
    "API_TOKEN": "",
    "MASTER_URL": None,
    # route serving the payload of a file-typed field, reversed with its file id
    "FILE_URL_NAME": None,
}

CONFIG.update(**getattr(settings, "FLEX_FIELDS_CONFIG", {}))
for entry in ["API_AUTHENTICATION_CLASSES", "API_PERMISSION_CLASSES"]:
    CONFIG[entry] = [import_string(m) for m in CONFIG[entry]]
