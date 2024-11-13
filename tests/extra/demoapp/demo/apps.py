from django.apps import AppConfig

from hope_flex_fields.attributes.registry import attributes_registry

from .strategy import MyHandler


class Config(AppConfig):
    name = "demo"

    def ready(self):
        attributes_registry.register(MyHandler)
