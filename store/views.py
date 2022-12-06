from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Product
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from .forms import UserRegisterForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.mixins import UserPassesTestMixin

# Create your views here.


def index(request):
    return HttpResponse("<h1>Hello, this is the main page</h1>")

def dashboard(request):
    if request.user.is_superuser:
        products = Product.objects.all()
        context = { 'products': products }
        return render(request, 'store/dashboard.html', context)
    return redirect('store:products')

def products(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/products.html', context=context)


class ProductCreateView(UserPassesTestMixin, CreateView):
    """ Class-based view for creating a produc
    it checks whether user is staff, then allows accessing the form 'product_form.html'
    if user is not a staff, then it redirects to the products page
    """
    model = Product
    fields = ['name','price','desc','image','product_type']
    
    # redirects to the products page after adding a product
    def get_success_url(self):
        return reverse_lazy('store:products')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('store:login')


# Authentication related

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
