from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'store'
urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.products, name='products'),
    path('products/add/', views.ProductCreateView.as_view(), name='add_product'),
    path('products/update/<uuid:pk>/', views.ProductUpdateView.as_view(), name='update_product'),
    path('products/delete/<uuid:pk>/', views.ProductDeleteView.as_view(), name='delete_product'),

    path('register/', views.SignUpView.as_view(), name='register'),
    path('login/', views.MyLoginView.as_view(),name='login'),
    path('logout/', views.logout_view, name='logout'),


]

# need to add to load images
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
