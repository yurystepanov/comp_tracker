from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    # product groups
    path('', views.ProductGroupListView.as_view(), name='product_group_list'),
    # all products
    path('list', views.ProductListView.as_view(), name='products'),
    # product list by group
    path('group/<int:id>/', views.ProductListView.as_view(), name='product_list_by_id'),
    path('group/<int:id>/<slug:slug>/', views.ProductListView.as_view(), name='product_list'),
    # product detail
    path('<int:pk>/', views.ProductDetailView.as_view(), name="product_detail_by_id"),
    path('<int:pk>/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]
