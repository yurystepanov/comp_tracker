from enum import Enum, auto

from rest_framework import serializers
from product.models import Product, ProductGroup, Brand, SpecificationValue, Specification, SpecificationGroup
from assembly.services import UserAssembly
from vendor.api.serializers import VendorLinkSerializerTiny


class StateOperations(Enum):
    ASSEMBLY = 'assembly_submit'
    FAVOURITES = 'favourites_submit'
    SUBSCRIPTION = 'subscription_submit'


class BrandSerializer(serializers.ModelSerializer):
    products = serializers.HyperlinkedIdentityField(view_name='brand-product-list',
                                                    lookup_url_kwarg='brand_pk',
                                                    read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'url', 'name', 'products']


class ProductGroupSerializer(serializers.HyperlinkedModelSerializer):
    products = serializers.HyperlinkedIdentityField(view_name='group-product-list',
                                                    lookup_url_kwarg='group_pk',
                                                    read_only=True)

    class Meta:
        model = ProductGroup
        fields = ['id', 'name', 'order', 'url', 'products']


class SpecificationGroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SpecificationGroup
        fields = ['id', 'name', 'order']


class SpecificationValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationValue
        fields = ['product', 'specification', 'value']


class ProductSpecificationSerializer(serializers.HyperlinkedModelSerializer):
    group_name = serializers.CharField(source='group.name')

    class Meta:
        model = Specification
        fields = ['name', 'group_name']

    def create(self, validated_data):
        group_name = validated_data.pop('group_name')
        name = validated_data.pop('name')

        specification_group = SpecificationGroup.objects().get_or_create(name=group_name)[0]
        specification = Specification.objects().get_or_create(name=name, group=specification_group)[o]

        return specification


class ProductSpecificationValueSerializer(serializers.ModelSerializer):
    specification = ProductSpecificationSerializer()

    class Meta:
        model = SpecificationValue
        fields = ['product', 'value', 'specification']

    def create(self, validated_data):
        group_name = ''
        product = validated_data.pop('product')
        value = validated_data.pop('value')
        specification = validated_data.pop('specification')
        group = specification.get('group')
        if group:
            group_name = group.get('name')
        name = specification.get('name')

        product_spec_group = SpecificationGroup.objects.get_or_create(name=group_name)[0]
        specification = Specification.objects.get_or_create(name=name, group=product_spec_group)[0]

        specification_value = SpecificationValue.objects.get_or_create(product=product,
                                                                       specification=specification,
                                                                       defaults={'value': value, }
                                                                       )

        return specification_value[0]


class ProductSerializer(serializers.ModelSerializer):
    specifications = serializers.HyperlinkedIdentityField(view_name='product-specification-list',
                                                          lookup_url_kwarg='product_pk',
                                                          read_only=True)
    links = VendorLinkSerializerTiny(many=True, read_only=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'url', 'name', 'brand', 'group', 'description_short', 'description', 'imageURL',
                  'specifications', 'price', 'links']


class StateOperationSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    operation = serializers.ChoiceField(required=True, choices=[e.value for e in StateOperations])
    state = serializers.BooleanField(required=True)

    def current_user(self):
        request = self.context.get('request', None)
        if request:
            return request.user

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist as e:
            raise serializers.ValidationError(e)

        return value

    def create(self, validated_data):
        product = Product.objects.get(id=validated_data['product_id'])

        if validated_data['operation'] == StateOperations.ASSEMBLY.value:
            request = self.context.get('request', None)
            if request:
                user_assembly = UserAssembly(request)
                if validated_data['state']:
                    user_assembly.add(product)
                else:
                    user_assembly.remove(product)

        elif validated_data['operation'] == StateOperations.FAVOURITES.value:
            if validated_data['state']:
                product.favourites.add(self.current_user())
            else:
                product.favourites.remove(self.current_user())
        else:
            assert validated_data['operation'] == StateOperations.SUBSCRIPTION.value
            if validated_data['state']:
                product.subscriptions.add(self.current_user())
            else:
                product.subscriptions.remove(self.current_user())
            pass

        return validated_data
