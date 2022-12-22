from django.urls import path
from . import views
app_name = 'order'

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<uuid:pk>', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:pk>',
         views.remove_from_cart, name='remove-from-cart'),
    path('increase_product_quantity/<int:pk>',
         views.increase_product_quantity, name='increase-product-quantity'),
    path('reduce_product_quantity/<int:pk>',
         views.reduce_product_quantity, name='reduce-product-quantity'),
    path('change_product_quantity/',
         views.change_product_quantity, name='change-product-quantity'),
    path('checkout', views.checkout, name="checkout"),

    path('apply_coupon/', views.coupon_apply, name='add-coupon'),
    path('remove_coupon/', views.coupon_remove, name='remove-coupon'),
    path('checkout/success/', views.PaymentSuccessView.as_view(), name='success'),
    path('checkout/failed/', views.PaymentFailedView.as_view(), name='failed'),
    path('api/checkout-session/<uuid:pk>',
         views.create_checkout_session, name='api_checkout_session'),
]
