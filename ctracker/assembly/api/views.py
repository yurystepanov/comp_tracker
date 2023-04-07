from rest_framework import viewsets

from assembly.models import Assembly
from assembly.api.serializers import AssemblySerializer


class AssemblyViewSet(viewsets.ModelViewSet):
    queryset = Assembly.objects.all()
    serializer_class = AssemblySerializer
    filterset_fields = ('name', 'owner')
