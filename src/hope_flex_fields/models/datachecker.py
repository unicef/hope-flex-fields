from collections.abc import Generator
from io import BytesIO
from typing import TYPE_CHECKING, Generic, TypeVar
from django.db import models
from django.utils.translation import gettext as _

from deprecation import deprecated

from ..utils import memoized_method
from ..xlsx import get_format_for_field, get_validation_for_field
from .base import ValidatorMixin
from .fieldset import Fieldset

if TYPE_CHECKING:
    from xlsxwriter import Format, Workbook
    from django import forms
    from ..forms import FlexForm
    from .flexfield import FlexField
    from ..fields import FlexFormMixin

    F = TypeVar("F", bound="FlexForm")


class DataCheckerManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class DataCheckerFieldset(models.Model):
    last_modified = models.DateTimeField(auto_now=True)
    checker = models.ForeignKey("DataChecker", on_delete=models.CASCADE, related_name="members")
    fieldset = models.ForeignKey(Fieldset, on_delete=models.CASCADE)
    prefix = models.CharField(max_length=30, blank=True, default="")
    order = models.PositiveSmallIntegerField(default=0)
    group = models.CharField(max_length=32, null=True, blank=True)
    override_group_default_value = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.checker.name}"


class DataChecker(ValidatorMixin, models.Model):
    """Used for complex validations to combine different fieldsets."""

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

    @memoized_method()
    def get_fields_with_groups(self) -> Generator[tuple["DataCheckerFieldset", "FlexField", str]]:
        fs: DataCheckerFieldset
        for fs in self.members.select_related("fieldset").all():
            for field in fs.fieldset.get_fields():
                if fs.override_group_default_value:
                    effective_group = fs.group if fs.group and fs.group.strip() else ""
                else:
                    effective_group = fs.fieldset.group

                yield fs, field, effective_group

    @memoized_method()
    def get_fields(self) -> Generator["FlexField"]:
        fs: DataCheckerFieldset
        for fs in self.members.select_related("fieldset").all():
            # for field in fs.fieldset.fields.select_related("definition").filter():
            for field in fs.fieldset.get_fields():
                yield fs, field

    @memoized_method()
    def get_field(self, name) -> "FlexField":
        for __, field in self.get_fields():
            if field.name == name:
                return field
        return None

    @deprecated("0.6.3", details="uses get_form_class()")
    def get_form(self) -> "Generic[F]":
        return self.get_form_class()

    def get_form_class(self) -> "Generic[F]":
        from ..forms import FlexForm

        fields: dict[str, forms.Field] = {}
        field: "FlexField"
        # for fs in self.members.select_related("fieldset").all():
        #     for field in fs.fieldset.fields.select_related("definition").filter():
        for fs, field in self.get_fields():
            fld: FlexFormMixin = field.get_field()
            label = ((fld.flex_field.attributes or {}).get("label") or "").strip() or field.name
            if "%s" in fs.prefix:
                fld.label = fs.prefix % label.replace("%", "%%")
                full_name = fs.prefix % field.name
            else:
                fld.label = f"{fs.prefix}{label}"
                full_name = f"{fs.prefix}{field.name}"

            fields[full_name] = fld
        form_class_attrs = {"datachecker": self, "validator": self, **dict(sorted(fields.items()))}
        return type(f"{self.name}DataCheckerForm", (FlexForm,), form_class_attrs)


def create_xls_importer(dc: "DataChecker") -> BytesIO:
    import xlsxwriter

    out = BytesIO()

    with xlsxwriter.Workbook(out, {"in_memory": True, "default_date_format": "yyyy/mm/dd"}) as workbook:
        worksheet = workbook.add_worksheet("Template")
        header_format = _get_header_format(workbook)

        for i, (fs, field) in enumerate(dc.get_fields()):
            prefixed_name = fs.prefix % field.name if "%s" in fs.prefix else f"{fs.prefix}{field.name}"
            worksheet.write(0, i, prefixed_name, header_format)

            col = chr(ord("A") + i)
            cell_format = _get_cell_format(workbook, field)
            worksheet.set_column(f"{col}1:{col}9999999", 40, cell_format)

            if v := get_validation_for_field(field):
                worksheet.data_validation("A1:Z9999", v)

    out.seek(0)
    return out


def _get_cell_format(workbook: "Workbook", field: "FlexField") -> "Format | None":
    fmt = get_format_for_field(field)
    if fmt:
        return workbook.add_format(fmt)
    return None


def _get_header_format(workbook: "Workbook") -> "Format":
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
    return header_format
