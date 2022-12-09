from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product
from .models import OrderItem, Order
# Create your views here.


def cart(request):
    customer_order = Order.objects.filter(
        customer=request.user, complete=False)

    customer_items = OrderItem.objects.filter(
        order_id__in=customer_order)

    context = {"orders": customer_order, "items": customer_items}

    return render(request, 'order/cart.html', context)


def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    order, created = Order.objects.get_or_create(
        customer=request.user, complete=False)
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product
    )
    order_item.quantity += 1
    order_item.save()

    return redirect("store:products")
