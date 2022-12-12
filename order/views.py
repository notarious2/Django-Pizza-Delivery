from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product
from users.models import Customer
from .models import OrderItem, Order
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
# Create your views here.


def cart(request):
    # checking if current user is authenticated/customer, if not customer will be created based on device id
    if request.user.is_authenticated:
        customer = request.user.customer
    else:
        customer, created = Customer.objects.get_or_create(
            device=request.COOKIES['device'])

    customer_order = Order.objects.filter(
        customer=customer, complete=False)

    # in case user visits cart directly  without adding any item
    if customer_order.exists():
        customer_items = OrderItem.objects.filter(
            order_id__in=customer_order)
        customer_order = customer_order[0]
    else:
        customer_order, customer_items = None, None

    # any not completed order is supposed to be a cart (session)

    context = {"order": customer_order, "items": customer_items}

    return render(request, 'order/cart.html', context)


@require_POST
def add_to_cart(request, pk):
    """
    adding one item to cart, if cart is empty order and order
    item will be created
    if user is not registered, device id from the cookies is used
    """
    product = get_object_or_404(Product, pk=pk)

    # checking if current user is authenticated/customer, if not customer will be created based on device id
    if request.user.is_authenticated:
        customer = request.user.customer
    else:
        customer, created = Customer.objects.get_or_create(
            device=request.COOKIES['device'])

    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product
    )
    order_item.quantity += 1
    order_item.save()

    # redirects to the same page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@require_POST
def remove_from_cart(request, pk):
    """
    removing product from the cart
    """
    product = get_object_or_404(Product, pk=pk)
    # checking if current user is authenticated/customer, if not customer will be created based on device id
    if request.user.is_authenticated:
        customer = request.user.customer
    else:
        customer, created = Customer.objects.get_or_create(
            device=request.COOKIES['device'])

    # order query set
    order_qs = Order.objects.filter(
        customer=customer, complete=False)
    if order_qs.exists():
        print("order exists")
        order = order_qs[0]
        order_item = OrderItem.objects.filter(order=order, product=product)
        order_item.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@require_POST
def reduce_product_quantity(request, pk):
    """
    reduce item quantity in the cart by one,
    if quantity becomes negative whole OrderItem gets deleted
    """
    product = get_object_or_404(Product, pk=pk)

    # checking if current user is authenticated/customer, if not customer will be created based on device id
    if request.user.is_authenticated:
        customer = request.user.customer
    else:
        customer, created = Customer.objects.get_or_create(
            device=request.COOKIES['device'])

    # order query set
    order_qs = Order.objects.filter(
        customer=customer, complete=False)
    if order_qs.exists():
        order = order_qs[0]
        order_item = OrderItem.objects.filter(order=order, product=product)[0]
        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
        else:
            order_item.delete()
    return redirect("order:cart")


def checkout(request):
    # checking if current user is authenticated/customer, if not customer will be created based on device id
    if request.user.is_authenticated:
        customer = request.user.customer
    else:
        customer, created = Customer.objects.get_or_create(
            device=request.COOKIES['device'])
    # order query set
    order_qs = Order.objects.filter(
        customer=customer, complete=False)
    # if order exists, get all order items
    if order_qs.exists():
        order = order_qs[0]
        order_items = OrderItem.objects.filter(order=order)
        print("Order Items", order_items)
        for item in order_items:
            print("PRODUCT NAME", item.product.name)
        print("TOTAL Q", order.get_cart_items)
        context = {"order": order, "order_items": order_items}
    return render(request, 'order/checkout.html', context=context)
