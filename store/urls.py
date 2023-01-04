from django.urls import path
from . import views

app_name = 'store'
urlpatterns = [
    path('', views.products, name='products'),
    path('pizza/', views.pizzas, name='pizzas'),
    path('drinks/', views.drinks, name='drinks'),
    path('sides/', views.sides, name='sides'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/add/', views.ProductCreateView.as_view(), name='add_product'),
    path('products/update/<uuid:pk>/',
         views.ProductUpdateView.as_view(), name='update_product'),
    path('products/delete/<uuid:pk>/',
         views.ProductDeleteView.as_view(), name='delete_product'),
]
