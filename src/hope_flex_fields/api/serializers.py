from rest_framework import serializers
from strategy_field.utils import fqn

from hope_flex_fields.models import DataChecker, FieldDefinition, Fieldset, FlexField


class BaseSerializer(serializers.ModelSerializer):
    pass


class FieldDefinitionSerializer(BaseSerializer):
    field_type = serializers.SerializerMethodField()

    class Meta:
        model = FieldDefinition
        fields = [
            "last_modified",
            "name",
            "description",
            "field_type",
            "attrs",
            "regex",
            "validation",
        ]

    def get_field_type(self, obj: FieldDefinition):
        return fqn(obj.field_type)


class FlexFieldSerializer(BaseSerializer):
    definition = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = FlexField
        fields = [
            "last_modified",
            "name",
            "description",
            "definition",
            "fieldset",
            "attrs",
            "regex",
            "validation",
        ]


class FieldsetSerializer(BaseSerializer):
    # fields = serializers.SlugRelatedField(
    #     many=True, read_only=True, slug_field="name"
    # )
    fields = FlexFieldSerializer(many=True)

    class Meta:
        model = Fieldset
        fields = ["last_modified", "name", "description", "extends", "fields"]


class DataCheckerSerializer(BaseSerializer):
    fieldsets = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = DataChecker
        fields = ["last_modified", "name", "description", "fieldsets"]
