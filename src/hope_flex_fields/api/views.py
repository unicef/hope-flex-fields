from django.http import HttpResponse

from rest_framework import viewsets

from ..config import CONFIG
from ..models import DataChecker, FieldDefinition, Fieldset, FlexField
from ..utils import dumpdata_to_buffer
from .serializers import DataCheckerSerializer, FieldDefinitionSerializer, FieldsetSerializer, FlexFieldSerializer


class Base:
    permission_classes = CONFIG["API_PERMISSION_CLASSES"]
    authentication_classes = CONFIG["API_AUTHENTICATION_CLASSES"]


class FieldDefinitionViewSet(Base, viewsets.ModelViewSet):
    queryset = FieldDefinition.objects.all().order_by("pk")
    serializer_class = FieldDefinitionSerializer


class FieldsetViewSet(Base, viewsets.ModelViewSet):
    queryset = Fieldset.objects.all().order_by("pk")
    serializer_class = FieldsetSerializer


class FlexFieldViewSet(Base, viewsets.ModelViewSet):
    queryset = FlexField.objects.all().order_by("pk")
    serializer_class = FlexFieldSerializer


class DataCheckerViewSet(Base, viewsets.ModelViewSet):
    queryset = DataChecker.objects.all().order_by("pk")
    serializer_class = DataCheckerSerializer


class SyncViewSet(Base, viewsets.ModelViewSet):

    def list(self, request, *args, **kwargs):
        return HttpResponse(dumpdata_to_buffer(), content_type="application/json")
