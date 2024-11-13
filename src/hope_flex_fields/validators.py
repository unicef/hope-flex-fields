import json

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from py_mini_racer import JSArray, JSObject, MiniRacer


class ReValidator(BaseValidator):
    @cached_property
    def rex(self):
        return self.limit_value

    def __call__(self, value):
        try:
            m = self.rex.match(str(value))
            if not m:
                raise ValueError()
        except ValueError:
            raise ValidationError("Invalid format. Allowed Regex is '%s'" % self.rex.pattern)
        return True


class JsValidator(BaseValidator):

    @property
    def code(self):
        return self.limit_value

    def __call__(self, value):
        ctx = MiniRacer()
        pickled = json.dumps(value or "")
        base = f"var value = {pickled};"
        ctx.eval(base)
        ret = ctx.eval(self.code)

        if isinstance(ret, JSArray):
            raise ValidationError(list(ret))

        if isinstance(ret, JSObject):
            errors = {s: k for s, k in ret.items()}
            raise ValidationError(errors)

        if isinstance(ret, str) and ret.strip() != "":
            raise ValidationError(_(ret))
        elif isinstance(ret, bool) and not ret:
            raise ValidationError(_("Please insert a valid value"))

        return True
