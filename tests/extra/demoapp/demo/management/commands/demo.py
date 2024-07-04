import logging
from typing import Any

from django import forms
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    requires_migrations_checks = False
    requires_system_checks = []

    def handle(self, *args: Any, **options: Any) -> None:
        from testutils.factories import (
            FieldDefinitionFactory,
            FieldsetFactory,
            FlexFieldFactory,
        )

        from hope_flex_fields.models import FieldDefinition

        hh = FieldsetFactory(name="household_with_individual")
        hh2 = FieldsetFactory(name="household_no_individual", extends=hh)
        # choice = FieldDefinition.objects.get(name="ChoiceField")
        string = FieldDefinition.objects.get(name="CharField")
        integer = FieldDefinition.objects.get(name="IntegerField")
        boolean = FieldDefinition.objects.get(name="BooleanField")
        RESIDENCE_STATUSES = ["CITIZEN", "REFUGEE", "MIGRANT", "IDP"]
        residence_status = FieldDefinitionFactory(
            name="ResidenceStatus",
            field_type=forms.ChoiceField,
            attrs={"choices": list(zip(RESIDENCE_STATUSES, RESIDENCE_STATUSES))},
        )

        FlexFieldFactory(
            fieldset=hh, name="residence_status_h_c", field=residence_status
        )
        FlexFieldFactory(fieldset=hh, name="consent_h_c", field=boolean)
        FlexFieldFactory(
            fieldset=hh,
            name="country_origin_h_c",
            field=string,
            attrs={"max_length": 3},
        )
        FlexFieldFactory(
            fieldset=hh, name="address_h_c", field=string, attrs={"max_length": 200}
        )

        FlexFieldFactory(
            fieldset=hh2,
            name="size_h_c",
            field=integer,
            attrs={"min_value": 1, "required": True},
        )
