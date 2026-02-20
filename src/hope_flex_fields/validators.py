import json

from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from py_mini_racer import JSArray, JSObject, MiniRacer, JSEvalException


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
            errors = dict(ret.items())
            raise ValidationError(errors)

        if isinstance(ret, str) and ret.strip() != "":
            raise ValidationError(_(ret))
        if isinstance(ret, bool) and not ret:
            raise ValidationError(_("Please insert a valid value"))

        return True


def fieldset_cross_validation(fieldset, data: dict) -> dict:
    code = (getattr(fieldset, "validation", "") or "").strip()
    if not code:
        return {}

    try:
        pickled = json.dumps(data or {}, cls=DjangoJSONEncoder, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        return {"-": [f"Validation data is not JSON-serializable: {e}"]}

    ctx = MiniRacer()
    ctx.eval(f"var data = {pickled};")

    try:
        ret = ctx.eval(f"(function(){{\n{code}\n}})()")
    except JSEvalException as e:
        return {"-": [f"JavaScript validation error: {e}"]}

    match ret:
        case True:
            return {}
        case JSObject() as obj:
            return dict(obj.items())
        case _:
            return {"-": ["Validation must return true or an errors object."]}
