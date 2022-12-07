from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Product
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView
from django.urls import reverse_lazy, reverse
from .forms import UserRegisterForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import user_passes_test

# Create your views here.


def index(request):
    return render(request, 'store/index.html')

@user_passes_test(lambda user: user.is_superuser, login_url="store:products")
def dashboard(request):
    """ using function-based view for dashboard as it promptly
    updates context data """
    products = Product.objects.all()
    context = { 'products': products }
    return render(request, 'store/dashboard.html', context)
    
def products(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/products.html', context=context)


class SuperUserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """A custom mixin that checks if user is both logged in and superuser, then allows accessing the template
    if user is not a supersuer, then it redirects to the products page
    """
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        return redirect('store:products')


class ProductCreateView(SuperUserRequiredMixin, CreateView):
    model = Product
    fields = ['name','price','desc','image','product_type']
    
    # redirects to the dashboard 
    def get_success_url(self):
        return reverse_lazy('store:dashboard')

class ProductUpdateView(SuperUserRequiredMixin, UpdateView):
    model = Product
    fields = ['name','price','desc','image','product_type']
    template_name_suffix = '_update_form'
    
    # redirects to the dashboard
    def get_success_url(self):
        return reverse_lazy('store:dashboard')
    
    
class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('store:dashboard')


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
