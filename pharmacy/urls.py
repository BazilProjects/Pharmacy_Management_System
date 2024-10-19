from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('all_sales_person', views.all_sales_person, name='all_sales_person'),
    path('sales-data/', views.sales_data, name='sales_data'),

    path('financial_statement', views.financial_statement, name='financial_statement'),
    path('all_drugs', views.all_products, name='all_drugs'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),


    path('all_categories', views.all_category, name='all_categories'),
    path('add-category/', views.add_category, name='add_category'),
    path('edit-category/<int:product_id>/', views.edit_category, name='edit_category'),


    path('all_supplier', views.all_supplier, name='all_supplier'),
    path('add-supplier/', views.add_supplier, name='add_supplier'),
    path('edit-supplier/<int:product_id>/', views.edit_supplier, name='edit_supplier'),



    path('all_pharmacy', views.all_pharmacy, name='all_pharmacy'),
    path('add-pharmacy/', views.add_pharmacy, name='add_pharmacy'),
    path('edit-pharmacy/<int:pharmacy_id>/', views.edit_pharmacy, name='edit_pharmacy'),
    path('delete-pharmacy/<int:pharmacy_id>/', views.delete_pharmacy, name='delete_pharmacy'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    


    path('all_sale', views.all_sales, name='all_sale'),
    path('check-drug/', views.check_drug_exists, name='check_drug_exists'),
    path('drug-suggestions/', views.drug_suggestions, name='drug_suggestions'),
    path('submit_form',views.submit_form,name="submit_form"),
    path('add-sale/', views.add_sales, name='add_sale'),
    path('edit-sale/<int:product_id>/', views.edit_sales, name='edit_sale'),
    
    # URL pattern for deleting a product
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product_search',views.product_search,name='product_search'),
    
    path('login/', views.login_view, name='login'),
    path('about_us/', views.about_us, name='about_us'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('salesperson/dashboard/', views.salesperson_dashboard, name='salesperson_dashboard'),
    path('signup_admin', views.admin_signup, name='admin_signup'),
    # Manager sign-up URL, takes group_id as a parameter
    path('manager/signup/<int:group_id>/', views.manager_signup, name='manager_signup'),
    #
    # Salesperson sign-up URL, takes group_id as a parameter
    path('salesperson/signup/<int:group_id>/', views.salesperson_signup, name='salesperson_signup'),
]
