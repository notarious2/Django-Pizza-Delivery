from django.shortcuts import render
from django.http import HttpResponse
from .models import Pizza

# Create your views here.


def index(request):
    return HttpResponse("<h1>Hello, this is the main page</h1>")


def products(request):
    pizzas = Pizza.objects.all()
    for pizza in pizzas:
        print(pizza.image.url)
    context = {'pizzas': pizzas}
    return render(request, 'store/products.html', context=context)
