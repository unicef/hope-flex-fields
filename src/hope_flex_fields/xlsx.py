from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hope_flex_fields.models import FlexField


xlsxwriter_options = {
    "DateField": {"num_format": "DD MMM-YY"},
    "DateTimeField": {"num_format": "DD MMD YY hh:mm"},
    "TimeField": {"num_format": "hh:mm"},
    "IntegerField": {"num_format": "#,##"},
    "PositiveIntegerField": {"num_format": "#,##"},
    "PositiveSmallIntegerField": {"num_format": "#,##"},
    "BigIntegerField": {"num_format": "#,##"},
    "DecimalField": {"num_format": "#,##0.00"},
    "BooleanField": {"num_format": "boolean"},
    "NullBooleanField": {"num_format": "boolean"},
    # 'EmailField': lambda value: 'HYPERLINK("mailto:%s","%s")' % (value, value),
    # 'URLField': lambda value: 'HYPERLINK("%s","%s")' % (value, value),
    "CurrencyColumn": {"num_format": '"$"#,##0.00);[Red]("$"#,##0.00)'},
}


def get_format_for_field(fld: "FlexField"):
    base_type = fld.base_type()
    # attrs = fld.get_merged_attrs()
    if base_type == "IntegerField":
        return {"num_format": "#,##"}


def get_validation_for_field(fld: "FlexField"):
    base_type = fld.base_type()
    attrs = fld.get_merged_attrs()
    if base_type == "IntegerField":
        base = {"validate": "integer"}
        if attrs.get("min_value"):
            base["minimum"] = attrs["min_value"]
            base["criteria"] = ">="
        if attrs.get("max_value"):
            base["max_value"] = attrs["max_value"]
            base["criteria"] = "<="

        if attrs.get("min_value") and attrs.get("max_value"):
            base["criteria"] = "between"
        return base
    elif base_type == "BooleanField":
        return {"validate": "list", "source": [True, False]}
    elif base_type == "DateField":
        return {}
    elif base_type == "ChoiceField":
        return {"validate": "list", "source": [m[0] for m in attrs.get("choices", [])]}
    return {}
