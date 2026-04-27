from django.urls import path
from . import views

urlpatterns = [

    path('', views.login_admin, name='login_admin'),
    path('logout/', views.logout_admin, name='logout_admin'),


    path("send-otp/", views.admin_send_otp, name="admin_send_otp"),
    path("verify-otp/", views.admin_verify_otp, name="admin_verify_otp"),
    path("reset-password/", views.admin_reset_password, name="admin_reset_password"),

    path('dashboard/', views.dashboard, name='admin_dashboard'),
    path('add-category/', views.add_category, name='add_category'),
    path('delete-category/<int:id>/', views.delete_category, name='delete_category'),
    path('delete-subcategory/<int:id>/', views.delete_subcategory, name='delete_subcategory'),
    path('edit-category/<int:id>/', views.edit_category, name='edit_category'),
    path('edit-subcategory/<int:id>/', views.edit_subcategory, name='edit_subcategory'),

    path('admin-products/', views.admin_products, name='admin_products'),
    path('edit-product/<int:id>/', views.edit_product, name='admin_edit_product'),
    path('delete-product/<int:id>/', views.delete_product, name='admin_delete_product'),

    path('admin-users/', views.admin_users, name='admin_users'),
    path('add-user/', views.add_user, name='add_user'),
    path('edit-user/<int:id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:id>/', views.delete_user, name='delete_user'),


    path('admin-artisans/', views.admin_artisans, name='admin_artisans'),
    path('add-artisan/', views.add_artisan, name='add_artisan'),
    path('edit-artisan/<int:id>/', views.edit_artisan, name='edit_artisan'),
    path('delete-artisan/<int:id>/', views.delete_artisan, name='delete_artisan'),

    path('check-email/', views.check_email, name='check_email'),

]