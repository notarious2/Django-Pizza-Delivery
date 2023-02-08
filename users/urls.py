from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.SignUpView.as_view(), name="register"),
    path("login/", views.MyLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("orders/", views.my_orders, name="my_orders"),
]
