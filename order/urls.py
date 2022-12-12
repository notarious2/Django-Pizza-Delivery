from django.urls import path
from . import views
app_name = 'order'

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<uuid:pk>', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<uuid:pk>',
         views.remove_from_cart, name='remove-from-cart'),
    path('reduce_product_quantity/<uuid:pk>',
         views.reduce_product_quantity, name='reduce-product-quantity'),
    path('checkout', views.checkout, name="checkout")

]
