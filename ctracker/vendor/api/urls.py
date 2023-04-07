from rest_framework_nested import routers
from django.urls import path, include

from . import views


router = routers.DefaultRouter()
router.register('vendors', views.VendorViewSet)
router.register('links', views.VendorLinkViewSet)
router.register('prices', views.VendorPriceViewSet)

link_router_vendor = routers.NestedSimpleRouter(router, r'vendors', lookup='vendor')
link_router_vendor.register(
    r'links',
    views.VendorLinkViewSet,
    basename='vendor-link'
)

price_router_vendor = routers.NestedSimpleRouter(router, r'vendors', lookup='vendor')
price_router_vendor.register(
    r'prices',
    views.VendorPriceViewSet,
    basename='vendor-price'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(link_router_vendor.urls)),
    path('', include(price_router_vendor.urls)),
]
