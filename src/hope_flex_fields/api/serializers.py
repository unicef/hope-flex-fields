from rest_framework import serializers
from strategy_field.utils import fqn

from hope_flex_fields.models import FieldDefinition


class FieldDefinitionSerializer(serializers.HyperlinkedModelSerializer):
    field_type = serializers.SerializerMethodField()

    class Meta:
        model = FieldDefinition
        fields = ["name", "description", "field_type", "attrs", "regex", "validation"]

    def get_field_type(self, obj):
        return fqn(obj)
