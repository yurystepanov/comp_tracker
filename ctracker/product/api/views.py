from rest_framework import viewsets, mixins, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from product.models import Product, ProductGroup, Brand, SpecificationValue, \
    annotate_queryset_with_price
from .serializers import (ProductSerializer, ProductGroupSerializer, BrandSerializer,
                          ProductSpecificationValueSerializer, StateOperationSerializer, StateOperations)

from product.filters import ProductFilterSet


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    queryset = queryset.select_related('brand', 'group')

    serializer_class = ProductSerializer

    filterset_class = ProductFilterSet
    group_id = None

    def get_queryset(self):
        group_id = self.kwargs.get("group_pk")

        self.queryset = annotate_queryset_with_price(self.queryset, show_unavaliable=True)

        self.queryset = self.queryset.select_related('brand', 'group')
        self.queryset = self.queryset.prefetch_related('links')

        if group_id:
            try:
                product_group = ProductGroup.objects.get(id=group_id)
            except ProductGroup.DoesNotExist:
                raise NotFound('A group with this id does not exist')
            self.group_id = product_group.id
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
    queryset = ProductGroup.objects.exclude(id=12)
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

        # with open(file='log.txt', mode='a') as f:
        # f.writelines('' + "\n")
        #     f.write(json.dumps(request.data) + "\n")
        #     f.writelines('' + "\n")
        #     f.write(json.dumps(serializer.errors) + "\n")

        if not valid:
            raise ValueError

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class StateOperationPermission(BasePermission):
    def has_permission(self, request, view):
        if request.data.get('operation', None) == StateOperations.ASSEMBLY.value:
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
