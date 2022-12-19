from django.shortcuts import render, redirect
from .models import Product
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator

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
    # get the keywords from the search field to alter products list
    product_name = request.GET.get('product')
    if product_name != '' and product_name is not None:
        products = products.filter(name__icontains=product_name)
    else:
        # if no item is searched input value is empty
        product_name = ""

    # pagination
    paginator = Paginator(products, 2)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    # search_string is used to display input value as searched product
    context = {'products': products,
               "search_string": product_name}
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
