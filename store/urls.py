from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.products, name='products'),
]

# need to add to load images
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
