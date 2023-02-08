from django.urls import path
from . import views

app_name = "store"
urlpatterns = [
    path("", views.products, name="products"),
    path("pizza/", views.pizzas, name="pizzas"),
    path("drinks/", views.drinks, name="drinks"),
    path("sides/", views.sides, name="sides"),
]
