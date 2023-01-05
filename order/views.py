from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product, ProductVariant, Size
from users.models import Customer
from .models import OrderItem, Order, Coupon, ShippingAddress, PickUpDetail
from .forms import CouponApplyForm
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages
import stripe
from django.conf import settings
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponseNotFound, JsonResponse, HttpResponse
import requests
import json
import datetime
from django.utils.timezone import make_aware

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
    adding item to cart from the main page, 
    if cart is empty order and order item will be created
    if user is not registered, device id from the cookies is used
    """
    product = get_object_or_404(Product, pk=pk)
    # getting product quantity
    quantity = int(json.loads(request.body)['quantity'])

    # getting product variation
    if product.has_variants:
        size = json.loads(request.body)['size']
        size = Size.objects.get(name=size)
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
        variation=variation,
    )
    order_item.quantity += quantity
    order_item.save()
    order.save()  # to update modified field of order model
    return JsonResponse({'cart_total': order.get_cart_items})


@require_POST
def remove_from_cart(request, pk):
    """
    removing product from the cart
    """
    order_item = get_object_or_404(OrderItem, pk=pk)
    order_item.delete()
    # save corresponding order to update modified date field
    order_item.order.save()
    # redirects to the same page
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
    # save corresponding order to update modified date field
    order_item.order.save()

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
    # save corresponding order to update modified date field
    order_item.order.save()
    return redirect("order:cart")


@require_POST
def change_product_quantity(request):
    quantity = request.POST.get('quantity')
    order_item_id = request.POST.get("orderItemId")
    order_item = get_object_or_404(OrderItem, pk=order_item_id)
    order_item.quantity = quantity
    order_item.save()
    # save corresponding order to update modified date field
    order_item.order.save()
    return redirect("order:cart")


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
            # check stripe api id of the coupon
            stripe_api_id = coupon.stripe_api_id
            if stripe_api_id:
                # retrieve coupon from stripe
                get_coupon = requests.get("https://api.stripe.com/v1/promotion_codes/" + stripe_api_id,
                                          auth=(settings.STRIPE_SECRET_KEY, ""))
                if get_coupon.status_code == 200:
                    # Use the json module to load response into a dictionary.
                    response_dict = json.loads(get_coupon.text)
                    coupon_id = response_dict["coupon"]["id"]
                    # double check coupon ID
                    if coupon.stripe_coupon_id == coupon_id:
                        messages.success(request, 'Coupon applied')
                else:
                    raise ValueError('Coupon cannot be verified')
            else:
                raise ValueError('Coupon cannot be verified')
            # checking if current user is authenticated/customer,
            # if not customer will be created based on device id
            if request.user.is_authenticated:
                customer = request.user.customer
            else:
                customer, created = Customer.objects.get_or_create(
                    device=request.COOKIES['device'])
            order = Order.objects.get(
                customer=customer, complete=False)
            order.coupon = coupon
            order.save()
        except Coupon.DoesNotExist:
            messages.error(request, 'Promo code does not exist')
        except ValueError:
            messages.error(request, 'Coupon cannot be verified')

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


@require_POST
def checkout(request):
    # pass stripe publishable key for checkout session
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY

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

        context = {"order": order, "order_items": order_items,
                   "coupon_form": coupon_form,
                   "stripe_publishable_key": stripe_publishable_key}
    return render(request, 'order/checkout.html', context=context)

@require_POST
def cash_checkout(request, pk):
    """
    Finalizing order with deferred payment - Cash payment
    """
    order = get_object_or_404(Order, transaction_id=pk)
    order.payment_method = "cash"

    # load data from POST to check delivery method
    data = json.loads(request.body)
    delivery = data.pop("delivery")
    if delivery:
        order.delivery_method = "delivery"
        # populate ShippingAddress model
    else:
        order.delivery_method = "carryout"
        if data['urgency'] == 'custom':
            # change data format and make naive datetime object timezone aware
            data['pickup_date'] = make_aware(datetime.datetime.strptime(data['pickup_date'], '%Y-%m-%d %I:%M %p'))
        # populate PickUpDetails model
        pickup_details = PickUpDetail(order=order, **data)
        try:
            # validate PickUp details
            pickup_details.full_clean()
            # save now - will be adjusted after payment is complete
            pickup_details.save()
        except Exception as e:
            print(e)
            # Collect errors and return Unprocessable Entity HTTP response 
            errors = []
            for key, value in e:
                validation_error = key.upper() + " " + value[0]
                errors.append(validation_error)
            return JsonResponse({"errors": errors}, status=422)
    
    # save order to apply payment and delivery methods
    order.complete = True
    order.save()
    # return redirect('order:cash-success')
    # return redirect(request, 'order/payment_success.html')
    return redirect(request.build_absolute_uri(reverse('order:success'))+"?cash=true")

@require_POST
def create_checkout_session(request, pk):
    """
    Stripe payment gateway for Online payment checkout
    """
    # get order by transaction_id
    order = get_object_or_404(Order, transaction_id=pk)
    # change order payment method to Online
    order.payment_method = "online"
    # load data from body and create address object
    data = json.loads(request.body)
    # get delivery status
    delivery = data.pop("delivery")
    print("delivery", delivery)
    print("DATA", data)
    if delivery:
        # change order delivery method to 'delivery'
        order.delivery_method = "delivery"
        # populate shipping address model
        shipping_address = ShippingAddress(order=order, **data)
        # manually trigger fields validation
        try:
            # validate data
            shipping_address.full_clean()
            # save now - will be adjusted after payment is complete
            shipping_address.save()
            # shipping id that will be passed as a url parameter
            shipping_id = shipping_address.id
        except Exception as e:
            # Collect errors and return Unprocessable Entity HTTP response 
            errors = []
            for key, value in e:
                validation_error = key.upper() + " " + value[0]
                errors.append(validation_error)
            return JsonResponse({"errors": errors}, status=422)
    else:
        # if carryout
        # change order delivery method to 'carryout'
        order.delivery_method = "carryout"
        
        if data['urgency'] == 'custom':
            # change data format and make naive datetime object timezone aware
            data['pickup_date'] = make_aware(datetime.datetime.strptime(data['pickup_date'], '%Y-%m-%d %I:%M %p'))
        # populate PickUpDetails model
        pickup_details = PickUpDetail(order=order, **data)
        try:
            # validate PickUp details
            pickup_details.full_clean()
            # save now - will be adjusted after payment is complete
            pickup_details.save()
            # pickup id that will be passed as a url parameter
            carryout_id = pickup_details.id
        except Exception as e:
            print(e)
            # Collect errors and return Unprocessable Entity HTTP response 
            errors = []
            for key, value in e:
                validation_error = key.upper() + " " + value[0]
                errors.append(validation_error)
            return JsonResponse({"errors": errors}, status=422)
    # save order to apply payment and delivery methods
    order.save()

    print("order", order.delivery_method, order.payment_method)
    # check if order has coupon
    if order.coupon:
        coupon_id = order.coupon.stripe_coupon_id
    else:
        coupon_id = None

    order_items = OrderItem.objects.filter(order=order)
    if order_items.exists():
        # array consisting of products that will be displayed in stripe payment page
        line_items = []
        for item in order_items:
            # show item size in the product name conditional on presence of product variants
            if item.product.has_variants:
                product_name = f"{item.product.name} ({item.variation.size})"
            else:
                product_name = item.product.name
            line_items.append(
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product_name,
                        },
                        'unit_amount': int(item.get_item_price*100),
                    },
                    'quantity': item.quantity,
                }
            )
    # change success url based on delivery/carryout status
    if delivery:
        success_url = request.build_absolute_uri(
            reverse('order:success'))+"?session_id={CHECKOUT_SESSION_ID}"+"&shipping_id=" + str(shipping_id)
    else:
        success_url = request.build_absolute_uri(
            reverse('order:success'))+"?session_id={CHECKOUT_SESSION_ID}"+"&carryout_id=" + str(carryout_id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
        customer_email=data["email"],
        payment_method_types=['card'],
        line_items=line_items,
        discounts=[{
            'coupon': coupon_id,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=request.build_absolute_uri(
            reverse('order:failed')),
        )
    return JsonResponse({'sessionId': checkout_session.id})



class PaymentSuccessView(TemplateView):
    template_name = 'order/payment_success.html'
    def get(self, request, *args, **kwargs):
        if not request.GET.get('cash'):
            session_id = request.GET.get('session_id')
            shipping_id = request.GET.get('shipping_id')
            carryout_id = request.GET.get('carryout_id')
            print("shipping_id", shipping_id)
            print("carryout_id", carryout_id)
            if session_id is None:
                return HttpResponseNotFound()
            # session = stripe.checkout.Session.retrieve(session_id)

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
                order.complete = True
                order.paid = True
                order.save()
            # clear previously created shipping/carryout models pertaining to the order
            if shipping_id:
                # get all shippings that contain order id and delete excluding current shipping address
                existing_shippings = ShippingAddress.objects.filter(
                    order=order).exclude(id=int(shipping_id))
                existing_shippings.delete()
                # delete all PickUpDetails pertaining to the order
                PickUpDetail.objects.filter(order=order).delete()
            elif carryout_id:
                # get all PickupDetails that contain order id and delete excluding current shipping address
                existing_pickup_details = PickUpDetail.objects.filter(
                    order=order).exclude(id=int(carryout_id))
                existing_pickup_details.delete()
                # delete all shippings pertaining to the order
                ShippingAddress.objects.filter(order=order).delete()
            else:
                return HttpResponseNotFound()
        return render(request, self.template_name)


class PaymentFailedView(TemplateView):
    template_name = 'order/payment_failed.html'
