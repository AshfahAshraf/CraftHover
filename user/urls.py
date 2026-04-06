from django.urls import path
from .import views
from .views import generate_description_api
urlpatterns = [
    
      path("register",views.index,name='register'),
      path("send-otp/<str:user_type>/", views.send_otp, name="send_otp"),
      path("verify-otp/", views.verify_otp, name="verify_otp"),        
      path("reset-password/", views.reset_password, name="reset_password"),
      path('terms_conditons',views.terms_conditon,name='terms_conditons'),
      
      path('privacy_policy',views.privacy_policy,name='privacy_policy'),
      path("navbar",views.navbar,name="navbar"),
      path('search/', views.search, name='search'),
      path('logout/', views.logout_view, name='logout'),
      path("footer",views.footer,name="footer"),

      path('',views.home,name="home"),
      path('category/<int:category_id>/', views.category_products, name='category_products'),
      path('about_us',views.aboutus,name="about_Us"),
      path('contact',views.contact,name='contact'),
      path('cart',views.cart_view,name="cart"),

      path("add-to-cart/<int:product_id>/",views.add_to_cart, name="add_to_cart"),
      path("remove-cart/<int:cart_id>/",views.remove_from_cart, name="remove_cart"),
      path("increase/<int:cart_id>/",views.increase_quantity, name="increases"),
      path('decrease/<int:cart_id>/',views.decrease_quantity, name="decreases"),
      path("place-order/", views.place_order, name="place_order"),
      
      path("order-success/", views.order_success, name="order_success"),
      path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
      path('wishlist/', views.wishlist_view, name='wishlist'),
      path('remove-wishlist/<int:wishlist_id>/', views.remove_wishlist, name='remove_wishlist'),
      path('wishlist-to-cart/<int:wishlist_id>/', views.wishlist_to_cart, name='wishlist_to_cart'),
      
      path('my_account',views.my_account,name="my_account"),
      path('address',views.address,name='address'),
      path('change_password',views.change_password,name="change_password"),
      path('faq',views.faq,name="faq"),
      path('return_refund',views.return_refund,name="return_refund"),
      
      path('shipping_info',views.shipping_info,name="shipping_info"),
      path('orders',views.orders,name="order"),
      path('cancel-order/<int:order_id>/',views.cancel_order,name="cancel_order"),
      path('seller_home',views.seller_home,name="seller_home"),
      path('artisan_register',views.artisan_register,name="artisan_register"),
      
      path("artisan-login/",views.artisan_login,name="artisan_login"),
      path('artisan_dashboard',views.artisan_dashboard,name="artisan_dashboard"),
      path("artisan_products/", views.artisan_products, name="artisan_products"),
      path("add_product/", views.add_product, name="add_product"),
      path('generate-description/',generate_description_api),
      
      path("Artisan_edit_product/<int:id>/", views.Artisan_edit_product, name="edit_product"),
      path("delete_product/<int:id>/", views.delete_product, name="delete_product"),
      path("artisan/orders/", views.artisan_orders, name="artisan_orders"),
      path('products/<int:subcategory_id>/', views.product_list, name='product_list'),
      path('product/<int:product_id>/', views.product_detail, name='product_detail'), 
      
      path("artisan_profile/", views.artisan_profile, name="artisan_profile"),
      path("artisan_logout/", views.artisan_logout, name="artisan_logout"),
      path('artisan/complaints/', views.artisan_complaints, name='artisan_complaints'),
      path('complaint/update/<int:id>/', views.update_complaint, name='update_complaint'),




] 
