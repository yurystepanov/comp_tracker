from rest_framework import viewsets
from rest_framework.exceptions import NotFound

from django_filters import rest_framework as filters
from django.contrib.contenttypes.models import ContentType

from vendor.api.serializers import VendorSerializer, VendorLinkSerializer, VendorPriceSerializer
from vendor.models import Vendor, VendorLink, VendorPrice


class VendorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['name']


class VendorLinkFilter(filters.FilterSet):

    def is_valid(self):
        if len(self.data):
            self.data._mutable = True
            if self.data.get('target_ct') == 'product' or self.data.get('target_ct') == 'productgroup':
                self.data['target_ct'] = ContentType.objects.get_by_natural_key('product',
                                                                                self.data.get('target_ct')).id
            self.data._mutable = False

        return super().is_valid()

    class Meta:
        model = VendorLink
        fields = ('vendor', 'external_id', 'target_id', 'target_ct')


class VendorLinkViewSet(viewsets.ModelViewSet):
    queryset = VendorLink.objects.all()
    serializer_class = VendorLinkSerializer
    filterset_class = VendorLinkFilter

    def get_queryset(self):
        vendor_id = self.kwargs.get("vendor_pk")
        if vendor_id:
            try:
                vendor = Vendor.objects.get(id=vendor_id)
            except Vendor.DoesNotExist:
                raise NotFound('A vendor with this id does not exist')
            return self.queryset.filter(vendor=vendor)

        return self.queryset


class VendorPriceViewSet(viewsets.ModelViewSet):
    queryset = VendorPrice.objects.all()
    queryset = queryset.select_related('vendor', 'product')
    serializer_class = VendorPriceSerializer
    filterset_fields = ['vendor', 'product', 'date', 'is_current']

    def get_queryset(self):
        vendor_id = self.kwargs.get("vendor_pk")
        if vendor_id:
            try:
                vendor = Vendor.objects.get(id=vendor_id)
            except Vendor.DoesNotExist:
                raise NotFound('A vendor with this id does not exist')
            return self.queryset.filter(vendor=vendor)

        return self.queryset
