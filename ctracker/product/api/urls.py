from django.urls import path, include
from rest_framework_nested import routers

from . import views
from vendor.api.urls import router as vendor_router
from assembly.api.urls import router as assembly_router

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('groups', views.ProductGroupViewSet)
router.register('brands', views.BrandViewSet)
router.register('specifications', views.SpecificationValueViewSet)

router.registry.extend(vendor_router.registry)
router.registry.extend(assembly_router.registry)

product_router_group = routers.NestedSimpleRouter(router, r'groups', lookup='group')
product_router_group.register(
    r'products',
    views.ProductViewSet,
    basename='group-product'
)

product_router_brand = routers.NestedSimpleRouter(router, r'brands', lookup='brand')
product_router_brand.register(
    r'products',
    views.ProductViewSet,
    basename='brand-product'
)

product_router_specifications = routers.NestedSimpleRouter(router, r'products', lookup='product')
product_router_specifications.register(
    r'specifications',
    views.SpecificationValueViewSet,
    basename='product-specification'
)

# router.register('specification_values', views.SpecificationValueViewSet)
# router.register('specification_groups', views.SpecificationGroupViewSet)

urlpatterns = [
    # path('products/',
    #      views.ProductListView.as_view(),
    #      name='product_list'),
    # path('products/<pk>/',
    #      views.ProductDetailView.as_view(),
    #      name='product_detail'),
    # path('products/', Pro)
    path('', include(router.urls)),
    path('', include(product_router_group.urls)),
    path('', include(product_router_brand.urls)),
    path('', include(product_router_specifications.urls)),
    path('state_operation', views.StateOperationView.as_view(),name='state_operation')
]
