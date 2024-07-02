import json

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.translation import gettext as _

from py_mini_racer import JSArray, JSObject, MiniRacer


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

        # try:
        #     ret = jsonpickle.decode(result)
        # except (JSONDecodeError, TypeError):
        #     ret = result

        if isinstance(ret, JSArray):
            raise ValidationError(list(ret))

        if isinstance(ret, JSObject):
            errors = {s: k for s, k in ret.items()}
            raise ValidationError(errors)

        if isinstance(ret, str):
            raise ValidationError(_(ret))
        elif isinstance(ret, bool) and not ret:
            raise ValidationError(_("Please insert a valid value"))

        return True
