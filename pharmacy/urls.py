from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('salesperson/dashboard/', views.salesperson_dashboard, name='salesperson_dashboard'),
    path('admin/add-product/', views.add_product, name='add_product'),
]
