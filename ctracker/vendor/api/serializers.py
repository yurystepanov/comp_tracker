from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from vendor.models import Vendor, VendorLink, VendorPrice


class ContentTypeField(serializers.Field):
    def to_representation(self, obj):
        return obj.model

    def to_internal_value(self, data):
        return ContentType.objects.get(model=data)


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'url', 'name', 'description', 'website']


class VendorLinkSerializerTiny(serializers.ModelSerializer):
    class Meta:
        model = VendorLink
        fields = ['id', 'vendor', 'external_id']


class VendorLinkSerializer(serializers.ModelSerializer):
    target_ct = ContentTypeField()
    target_url = serializers.HyperlinkedRelatedField(view_name='product-detail',
                                                     lookup_field='target_id',
                                                     lookup_url_kwarg='pk',
                                                     read_only=True,
                                                     source='*')

    def to_representation(self, instance):
        self.fields['target_url'].view_name = f'{instance.target_ct.model}-detail'
        return super().to_representation(instance)

    class Meta:
        model = VendorLink
        fields = ['id', 'vendor', 'external_id', 'url', 'target_id', 'target_ct', 'target_url']


class VendorPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPrice
        fields = ['id', 'vendor', 'product', 'price', 'date', 'is_current', 'updated_at']
