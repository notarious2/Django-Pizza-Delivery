from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Product
from django.views.generic.edit import CreateView,UpdateView,DeleteView, FormView
from django.urls import reverse_lazy, reverse
from .forms import UserRegisterForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout

# Create your views here.


def index(request):
    return HttpResponse("<h1>Hello, this is the main page</h1>")


def products(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/products.html', context=context)

# Creating a new user

class SignUpView(CreateView):
  template_name = 'store/register.html'
  success_url = reverse_lazy('store:login')
  form_class = UserRegisterForm


class MyLoginView(LoginView):
    success_url = reverse_lazy('store:products')
    template_name='store/login.html'
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('store:products'))
        return super(LoginView, self).get(request, *args, **kwargs)

def logout_view(request):
    logout(request)
    return redirect('store:products')
