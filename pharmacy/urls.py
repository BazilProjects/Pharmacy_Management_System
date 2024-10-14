from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('salesperson/dashboard/', views.salesperson_dashboard, name='salesperson_dashboard'),
    path('admin/add-product/', views.add_product, name='add_product'),
    path('signup_admin', views.admin_signup, name='admin_signup'),
    # Manager sign-up URL, takes group_id as a parameter
    path('manager/signup/<int:group_id>/', views.manager_signup, name='manager_signup'),

    # Salesperson sign-up URL, takes group_id as a parameter
    path('salesperson/signup/<int:group_id>/', views.salesperson_signup, name='salesperson_signup'),
]
