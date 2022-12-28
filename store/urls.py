from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
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

# need to add to load images
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
