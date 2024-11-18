import logging
from typing import Any, Generator, Iterable

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Model
from django.utils.text import slugify

from django_regex.fields import RegexField
from django_regex.validators import RegexValidator

#
logger = logging.getLogger(__name__)


class BaseQuerySet(models.QuerySet["Model"]):

    def get(self, *args: Any, **kwargs: Any) -> "Model":
        try:
            return super().get(*args, **kwargs)
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist(
                "%s matching query does not exist. Using %s %s" % (self.model._meta.object_name, args, kwargs)
            )


class BaseManager(models.Manager["Model"]):
    _queryset_class = BaseQuerySet


class AbstractField(models.Model):
    last_modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=500, blank=True, null=True, default="")
    attrs = models.JSONField(default=dict, blank=True, null=False)
    regex = RegexField(blank=True, null=True, validators=[RegexValidator()])
    validation = models.TextField(blank=True, null=True, default="")
    slug = models.SlugField(blank=True, null=True, editable=False)

    class Meta:
        abstract = True

    @property
    def attributes(self):
        raise NotImplementedError

    @attributes.setter
    def attributes(self, value):
        raise NotImplementedError

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(
            *args,
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


class ValidatorMixin:
    def __init__(self, *args, **kwargs):
        self._primary_key_field_name = None
        self._master_fieldset = None
        self.form = None
        self.primary_keys = set()
        self.globals = {}
        # self._collect_values = []
        self._collected_values = {}
        super().__init__(*args, **kwargs)

    def set_primary_key_col(self, name: str):
        self._primary_key_field_name = name

    def set_master(self, fs: "ValidatorMixin", col_name: str):
        self._master_fieldset = fs
        self._master_fieldset_col = col_name

    def collect(self, *fields):
        for field_name in fields:
            self._collected_values[field_name] = []

    def collected(self, field_name):
        return self._collected_values[field_name]

    def is_duplicate(self, form):
        if self._primary_key_field_name:
            if pk := form.cleaned_data[self._primary_key_field_name]:
                if pk in self.primary_keys:
                    return f"{pk} duplicated"
            self.primary_keys.add(form.cleaned_data[self._primary_key_field_name])
            # self.primary_keys.add(str(pk).strip())

    def is_valid_foreignkey(self, form):
        if self._master_fieldset:
            fk = form.cleaned_data[self._master_fieldset_col]
            if fk not in self._master_fieldset.primary_keys:
                return f"'{fk}' not found in master"

    def validate_parent_child(self, errors, data):
        for field_name, field in self.form.fields.items():
            if field.flex_field.master and hasattr(field, "validate_with_parent"):
                parent_value = data.get(field.flex_field.master.name)
                value = data.get(field_name)
                try:
                    field.validate_with_parent(parent_value, value)
                except ValidationError as e:
                    if field_name not in errors:
                        errors[field_name] = str(e)
                    else:
                        errors[field_name].append(str(e))

        return errors

    def get_form_class(self):
        raise NotImplementedError

    def validate(
        self,
        data: Iterable,
        *,
        include_success: bool = False,
        fail_if_alien: bool = False,
    ):
        from hope_flex_fields.forms import FlexForm

        if not isinstance(data, (list, tuple, Generator)):
            data = [data]
        self.primary_keys = set()
        form_class: type[FlexForm] = self.get_form_class()
        known_fields = set(sorted(form_class.declared_fields.keys()))
        ret = {}
        for i, row in enumerate(data, 1):
            self.form: "FlexForm" = form_class(data=row)
            posted_fields = set(sorted(row.keys()))
            fields_errors = {}
            row_errors = []
            if fail_if_alien and (diff := posted_fields.difference(known_fields)):
                row_errors.append(f"Alien values found {diff}")
            if not self.form.is_valid():
                fields_errors.update(**self.form.errors)

            if err := self.is_duplicate(self.form):
                row_errors.append(err)
            if err := self.is_valid_foreignkey(self.form):
                row_errors.append(err)

            for field_name in self._collected_values.keys():
                self._collected_values[field_name].append(self.form.cleaned_data[field_name])
            if row_errors:
                fields_errors["-"] = row_errors
            self.validate_parent_child(fields_errors, row)

            if fields_errors:
                ret[i] = fields_errors
            elif include_success:
                ret[i] = "Ok"
        return ret
