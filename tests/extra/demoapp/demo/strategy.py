from typing import TYPE_CHECKING

from django import forms

import requests

from hope_flex_fields.attributes.abstract import AbstractAttributeHandler, AttributeHandlerConfig

if TYPE_CHECKING:
    from hope_flex_fields.types import Json


class MyHandlerConfig(AttributeHandlerConfig):
    url = forms.URLField()


class MyHandler(AbstractAttributeHandler):
    dynamic = True
    config_class = MyHandlerConfig

    def set(self, value: "Json"):
        self.owner.attrs = value

    def get(self) -> "Json":
        ret = requests.get("http://test.org/data/")
        data = ret.json()
        return self.owner.attrs | {"choices": [(n, n) for n in data["choices"]]}
