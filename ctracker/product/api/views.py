import json

from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import viewsets, mixins, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from product.models import Product, ProductGroup, Brand, SpecificationValue, SpecificationGroup
from .serializers import (ProductSerializer, ProductGroupSerializer, BrandSerializer,
                          ProductSpecificationValueSerializer, StateOperationSerializer, StateOperations)


class ProductFilter(filters.FilterSet):
    search = filters.CharFilter(field_name='search', method='filter_search', label='Search')
    pn = filters.CharFilter(field_name='pn', method='pn_search', label='Manufacturers P/N')

    class Meta:
        model = Product
        fields = ['name', 'group']

    def filter_search(self, qs, name, value):
        for item in value.split('~~'):
            qs = qs.filter(
                Q(name__contains=item) |
                Q(description_short__contains=item)
            )

        return qs

    def pn_search(self, qs, name, value):
        qs = qs.filter(specifications__value__contains=value,
                       specifications__specification__name='Код производителя')

        return qs


# class ProductListView(generics.ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#
#
# class ProductDetailView(generics.RetrieveAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    queryset = queryset.select_related('brand', 'group')

    # queryset = queryset.select_related('group')

    # specifications_qs = SpecificationValue.objects.select_related('specification', 'specification__group')
    #
    # queryset = queryset.prefetch_related(Prefetch('specifications', queryset=specifications_qs))

    serializer_class = ProductSerializer
    filterset_class = ProductFilter

    def get_queryset(self):
        group_id = self.kwargs.get("group_pk")
        if group_id:
            try:
                product_group = ProductGroup.objects.get(id=group_id)
            except ProductGroup.DoesNotExist:
                raise NotFound('A group with this id does not exist')
            return self.queryset.filter(group=product_group)

        brand_id = self.kwargs.get("brand_pk")
        if brand_id:
            try:
                brand = Brand.objects.get(id=brand_id)
            except Brand.DoesNotExist:
                raise NotFound('A brand with this id does not exist')
            return self.queryset.filter(brand=brand)

        return self.queryset


class ProductGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductGroup.objects.all()
    serializer_class = ProductGroupSerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filterset_fields = {'name': ['exact', 'contains'], }


class SpecificationValueViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = SpecificationValue.objects.all()
    serializer_class = ProductSpecificationValueSerializer

    def get_queryset(self):
        product_id = self.kwargs.get("product_pk")
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise NotFound('A product with this id does not exist')
            return self.queryset.filter(product=product)

        return self.queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        valid = serializer.is_valid(raise_exception=False)

        with open(file='log.txt', mode='a') as f:
            f.writelines('' + "\n")
            f.write(json.dumps(request.data) + "\n")
            f.writelines('' + "\n")
            f.write(json.dumps(serializer.errors) + "\n")

        if not valid:
            raise ValueError

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class StateOperationPermission(BasePermission):
    def has_permission(self, request, view):
        if request.data.get('operation', None) == StateOperations.ASSEMBLY:
            return True
        else:
            return bool(request.user and request.user.is_authenticated)


class StateOperationView(APIView):
    serializer_class = StateOperationSerializer
    permission_classes = [StateOperationPermission]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
