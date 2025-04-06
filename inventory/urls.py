from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.homepage, name='homepage'),  # Map the root URL to the homepage view
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),    path('cashier_pos/', views.cashier_pos, name='cashier_pos'),  # Cashier POS
    path('login/', views.user_login, name='user_login'),
    path('inventory_management/', views.inventory_management, name='inventory_management'),
    path('sales_report/', views.sales_report, name='sales_report'),
    path('add_item/', views.add_item, name='add_item'),
    path('category_management/', views.category_management, name='category_management'),    
    path('user_management/', views.user_management, name='user_management'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add_item/', views.add_item, name='add_item'),
    path('update_item/<int:item_id>/', views.update_item, name='update_item'),
    path('delete_item/<int:id>/', views.delete_item, name='delete_item'),
    path('item_autocomplete/', views.item_autocomplete, name='item_autocomplete'),
]

