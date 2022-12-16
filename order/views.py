from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product, ProductVariant, Size
from users.models import Customer
from .models import OrderItem, Order, Coupon
from .forms import CouponApplyForm
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages

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
            order_id__in=customer_order).order_by("product__name", "-variation__size")
        customer_order = customer_order[0]
    else:
        customer_order, customer_items = None, None


    # any not completed order is supposed to be a cart (session)

    context = {
        "order": customer_order, 
        "items": customer_items,
        }

    return render(request, 'order/cart.html', context)


@require_POST
def add_to_cart(request, pk):
    """
    adding item to cart from the main page, if cart is empty order and order
    item will be created
    if user is not registered, device id from the cookies is used
    """
    print("SIZE", request.POST.get('size'))

    product = get_object_or_404(Product, pk=pk)
    
    # getting product variation
    if product.has_variants:
        size = request.POST.get('size')
        size = Size.objects.get(name = size)
        variation = ProductVariant.objects.get(size=size, product=product) 
    else:
        variation = None
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
        product=product,
        variation=variation
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
    order_item = get_object_or_404(OrderItem, pk=pk)
    order_item.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@require_POST
def increase_product_quantity(request, pk):
    """
    adding +1 item inside the cart
    """
    
    # checking if current user is authenticated/customer, if not customer will be created based on device id
    # if request.user.is_authenticated:
    #     customer = request.user.customer
    # else:
    #     customer, created = Customer.objects.get_or_create(
    #         device=request.COOKIES['device'])

    order_item = get_object_or_404(OrderItem, pk=pk)

    order_item.quantity += 1
    order_item.save()

    # redirects to the same page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@require_POST
def reduce_product_quantity(request, pk):
    """
    reduce item quantity in the cart by one,
    if quantity becomes negative whole OrderItem gets deleted
    """

    # checking if current user is authenticated/customer, if not customer will be created based on device id
    # if request.user.is_authenticated:
    #     customer = request.user.customer
    # else:
    #     customer, created = Customer.objects.get_or_create(
    #         device=request.COOKIES['device'])

    # order query set
    order_item = get_object_or_404(OrderItem, pk=pk)
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
        # coupon form
        coupon_form = CouponApplyForm()
        context = {"order": order, "order_items": order_items, 'coupon_form': coupon_form,}
    return render(request, 'order/checkout.html', context=context)

@require_POST
def coupon_apply(request):
    now = timezone.now()
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code, 
            valid_from__lte=now, 
            valid_to__gte=now, 
            active=True)
            
            order = Order.objects.get(
                    customer=request.user.customer, complete=False)
            order.coupon = coupon
            order.save()

        except Coupon.DoesNotExist:
            print("PROMO CODE DOES NOT EXIST", code)
    return redirect('order:checkout')

@require_POST
def coupon_remove(request):
    """
    remove coupon from the cart
    """
    if request.method == "POST":
        order = Order.objects.get(
            customer=request.user.customer, complete=False)
        order.coupon = None
        order.save()
    return redirect('order:checkout')