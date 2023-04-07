from django.urls import path

from . import views

app_name = 'assembly'

urlpatterns = [
    path('list', views.AssemblyListView.as_view(), name='assembly_list'),
    path('<int:pk>/', views.AssemblyDetailView.as_view(), name="assembly_detail_by_id"),
    path('<int:pk>/<slug:slug>/', views.AssemblyDetailView.as_view(), name='assembly_detail'),

    path('user/list', views.UserAssemblyListView.as_view(), name='user_assembly_list'),
    path('user', views.user_assembly, name='user_assembly'),

    path('user/changeqty', views.change_product_qty, name='change_product_qty'),
    path('user/edit_user_assembly', views.edit_user_assembly, name='edit_user_assembly'),
    path('user/current_assembly', views.current_assembly, name='current_assembly'),
]
