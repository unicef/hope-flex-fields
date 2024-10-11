from io import BytesIO
from typing import TYPE_CHECKING

from django import forms
from django.db import models
from django.utils.translation import gettext as _

from ..fields import FlexFormMixin
from ..xlsx import get_format_for_field, get_validation_for_field
from .base import FlexForm, ValidatorMixin
from .fieldset import Fieldset

if TYPE_CHECKING:
    from .flexfield import FlexField


def create_xls_importer(dc: "DataChecker"):
    import xlsxwriter

    # pattern = xlsxwriter_options.get(
    #     fld.name, xlsxwriter_options.get(fld.base_type(), "general")
    # )
    # fmt = workbook.add_format({"num_format": pattern})

    out = BytesIO()
    workbook = xlsxwriter.Workbook(
        out, {"in_memory": True, "default_date_format": "yyyy/mm/dd"}
    )
    # locked = workbook.add_format({"locked": True})

    header_format = workbook.add_format(
        {
            "bold": False,
            "font_color": "black",
            "font_size": 22,
            "font_name": "Arial",
            "align": "center",
            "valign": "vcenter",
            "indent": 1,
        }
    )
    header_format.set_bg_color("#CFC122")
    header_format.set_locked(True)
    header_format.set_align("center")
    header_format.set_bottom_color("black")
    worksheet = workbook.add_worksheet()

    for i, fld in enumerate(dc.get_fields()):
        col = chr(ord("A") + i)
        worksheet.write(0, i, fld.name, header_format)
        f = None
        if fmt := get_format_for_field(fld):
            f = workbook.add_format(fmt)
        worksheet.set_column(f"{col}1:{col}9999999", 40, f)

        if v := get_validation_for_field(fld):
            worksheet.data_validation("A1:Z9999", v)

    # worksheet.protect("A1:AZZ1")
    # worksheet.unprotect_range("A2:Z999999")
    workbook.close()
    out.seek(0)
    return out, workbook


class DataCheckerManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class DataCheckerFieldset(models.Model):
    last_modified = models.DateTimeField(auto_now=True)
    checker = models.ForeignKey(
        "DataChecker", on_delete=models.CASCADE, related_name="members"
    )
    fieldset = models.ForeignKey(Fieldset, on_delete=models.CASCADE)
    prefix = models.CharField(max_length=30, blank=True, default="")
    order = models.PositiveSmallIntegerField(default=0)


class DataChecker(ValidatorMixin, models.Model):
    """Used for complex validations to combine different fieldsets"""

    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    fieldsets = models.ManyToManyField(Fieldset, through=DataCheckerFieldset)
    objects = DataCheckerManager()

    class Meta:
        verbose_name = _("DataChecker")
        verbose_name_plural = _("DataCheckers")

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    def get_fields(self):
        for fs in self.members.all():
            for field in fs.fieldset.fields.filter():
                yield field

    def get_form(self) -> "type[FlexForm]":
        fields: dict[str, forms.Field] = {}
        field: "FlexField"
        for fs in self.members.all():
            for field in fs.fieldset.fields.filter():
                fld: FlexFormMixin = field.get_field()
                fld.label = f"{fs.prefix}{field.name}"
                if "%s" in fs.prefix:
                    full_name = fs.prefix % field.name
                else:
                    full_name = f"{fs.prefix}{field.name}"

                fields[full_name] = fld
        form_class_attrs = {"DataChecker": self, **fields}
        return type(f"{self.name}DataChecker", (FlexForm,), form_class_attrs)
