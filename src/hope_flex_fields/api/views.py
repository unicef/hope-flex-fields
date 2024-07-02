from rest_framework import permissions, viewsets

from ..models import FieldDefinition
from .serializers import FieldDefinitionSerializer


class FieldDefinitionViewSet(viewsets.ModelViewSet):
    queryset = FieldDefinition.objects.all().order_by("pk")
    serializer_class = FieldDefinitionSerializer
    permission_classes = [permissions.IsAuthenticated]
