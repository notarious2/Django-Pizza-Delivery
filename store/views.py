from django.shortcuts import render, redirect
from .models import Product
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.decorators import user_passes_test

# Create your views here.


def index(request):
    return render(request, 'store/index.html')


@user_passes_test(lambda user: user.is_superuser, login_url="store:products")
def dashboard(request):
    """ using function-based view for dashboard as it promptly
    updates context data """
    products = Product.objects.all()
    context = {'products': products}
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
    fields = ['name', 'price', 'desc', 'image', 'product_type']

    # redirects to the dashboard
    def get_success_url(self):
        return reverse_lazy('store:dashboard')


class ProductUpdateView(SuperUserRequiredMixin, UpdateView):
    model = Product
    fields = ['name', 'price', 'desc', 'image', 'product_type']
    template_name_suffix = '_update_form'

    # redirects to the dashboard
    def get_success_url(self):
        return reverse_lazy('store:dashboard')


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('store:dashboard')
