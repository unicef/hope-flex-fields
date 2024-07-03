from django.utils.text import slugify


def namefy(value):
    return slugify(value).replace("-", "_")


def camelcase(value):
    if " " in value or "-" in value or "_" in value:
        value = value.replace("-", " ").replace("_", " ")
        return "".join(x for x in value.title() if not x.isspace())
    return value.capitalize()
