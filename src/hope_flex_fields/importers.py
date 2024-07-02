from django.core.exceptions import ValidationError

from hope_flex_fields.models import Fieldset


def validate_json(data, fieldset):
    fs: Fieldset = Fieldset.objects.get(name=fieldset)
    ret = []
    for r in data:
        try:
            fs.validate(r)
            ret.append("Ok")
        except ValidationError as e:
            ret.append(e.message_dict)
    return ret
