from django.urls import re_path,path
from .import views
from .views import generate_description_api
urlpatterns = [
    #register and login page
      path("register",views.index,name='register'),
      #email otp
      path("send-otp",views.send_otp,name="send_otp"),
      path("verify-otp",views.verify_otp,name="verify_otp"),
      path("reset-password",views.reset_password,name="reset_password"),

    
      re_path('^terms_conditons',views.terms_conditon,name='terms_conditons'),
      re_path('^privacy_policy$',views.privacy_policy,name='privacy_policy'),
      re_path("^navbar$",views.navbar,name="navbar"),
      path('logout/', views.logout_view, name='logout'),

      re_path("^footer$",views.footer,name="footer"),
      path('',views.home,name="home"),
      re_path('^about_us$',views.aboutus,name="about_Us"),
      re_path('^contact$',views.contact,name='contact'),

      #cart
      path('cart',views.cart_view,name="cart"),
      path("add-to-cart/<int:product_id>/",views.add_to_cart, name="add_to_cart"),
      path("remove-cart/<int:cart_id>/",views.remove_from_cart, name="remove_cart"),
      path("increase/<int:cart_id>/",views.increase_quantity, name="inreases"),
      path('decrease/<int:cart_id>/',views.decrease_quantity, name="decrease"),
      path('order-success/', views.order_success, name='order_success'),

    #wishlist
      path("wishlist/",views.wishlist_view, name="wishlist"),
      path("add-wishlist/<int:product_id>/",views.add_to_wishlist,name="add_wishlist"),
      path('remove-wishlist/<int:wishlist_id>/',views.remove_wishlist,name="remove_wishlist"),
      path("wishlist-to-cart/<int:wishlist_id>/",views.wishlist_to_cart,name='wishlist_to_cart'),


      re_path('^faq$',views.faq,name="faq"),
      re_path('^return_refund$',views.return_refund,name="return_refund"),
      re_path('^shipping_info$',views.shipping_info,name="shipping_info"),


      path('my_account',views.my_account,name="my_account"),
      path('address',views.address,name='address'),
      path('change_password',views.change_password,name="change_password"),

      path('orders',views.orders,name="order"),
      path('cancel-order/<int:order_id>/',views.cancel_order,name="cancel_order"),

      path('seller_home',views.seller_home,name="seller_home"),
      path('artisan_register',views.artisan_register,name="artisan_register"),
      path("artisan-login/",views.artisan_login,name="artisan_login"),
      path('artisan_dashboard',views.artisan_dashboard,name="artisan_dashboard"),
      path("artisan_products/", views.artisan_products, name="artisan_products"),
      path("add_product/", views.add_product, name="add_product"),
      path('generate-description/',generate_description_api),

      path("edit_product/<int:id>/", views.edit_product, name="edit_product"),
      path("delete_product/<int:id>/", views.delete_product, name="delete_product"),
      path("artisan/orders/", views.artisan_orders, name="artisan_orders"),
path('products/<int:subcategory_id>/', views.product_list, name='product_list'),
       path('product/<int:product_id>/', views.product_detail, name='product_detail'),  # ✅ NEW

    path("cancel-order/<int:order_id>/", views.cancel_order, name="cancel_order"),
    path("artisan_profile/", views.artisan_profile, name="artisan_profile"),
    path("artisan_logout/", views.artisan_logout, name="artisan_logout"),
    path("logout/", views.logout_view, name="logout"),
    path("example/", views.example, name="example"),



 ] 
