from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product, ProductVariant, Size
from users.models import Customer
from .models import OrderItem, Order, Coupon, ShippingAddress, PickUpDetail
from .forms import CouponApplyForm
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib import messages
import stripe
from django.conf import settings
from django.urls import reverse
from django.views.generic import TemplateView
from django.http.response import HttpResponseNotFound, JsonResponse
import json
import datetime


def get_customer_or_guest(request):
    """
    checking if current user is authenticated/customer,
    if not customer will be created based on device id
    """
    if request.user.is_authenticated:
        customer = request.user.customer
    else:
        customer, created = Customer.objects.get_or_create(
            device=request.COOKIES['device'])
    return customer


def cart(request):
    """
    Cart page. It contains information about only one order,
    which has not complete (complete=False) status.
    """
    try:
        customer = get_customer_or_guest(request)
    except:
        return redirect('store:products')

    customer_order = Order.objects.filter(
        customer=customer, complete=False)

    # in case user visits cart directly  without adding any item
    if customer_order.exists():
        customer_items = OrderItem.objects.filter(
            order_id__in=customer_order).order_by("product__name", "-variation__size")
        customer_order = customer_order[0]
    else:
        customer_order, customer_items = None, None

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

    try:
        customer = get_customer_or_guest(request)
    except:
        return redirect('store:products')

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
    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('order:cart')


@require_POST
def increase_product_quantity(request, pk):
    """
    adding +1 item to the cart
    this functionality is used inside the cart page
    """
    order_item = get_object_or_404(OrderItem, pk=pk)
    order_item.quantity += 1
    order_item.save()

    # save corresponding order to update modified date field
    order_item.order.save()

    # redirect to the same page
    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('order:cart')


@require_POST
def reduce_product_quantity(request, pk):
    """
    reduce item quantity in the cart by one,
    if quantity becomes negative whole OrderItem gets deleted
    """
    # order query set
    order_item = get_object_or_404(OrderItem, pk=pk)
    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order_item.delete()

    # save corresponding order to update modified date field
    order_item.order.save()

    # redirect to the same page
    return redirect('order:cart')


@require_POST
def change_product_quantity(request):
    """
    Change product quantity inside the cart - uses Ajax
    """
    quantity = request.POST.get('quantity')
    order_item_id = request.POST.get("orderItemId")
    order_item = get_object_or_404(OrderItem, pk=order_item_id)
    order_item.quantity = quantity
    order_item.save()
    # save order to update modified date field
    order_item.order.save()
    return redirect("order:cart")


@require_POST
def coupon_apply(request):
    """
    Applies the coupon inside checkout.
    From the coupon code it first retrieves Coupon from the database,
    then confirms it using Stripe Coupon ID from Stripe Coupon webhook
    """
    now = timezone.now()
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code,
                                        valid_from__lte=now,
                                        valid_to__gte=now,
                                        active=True)
            # check Coupon ID with stripe webhook
            stripe.api_key = settings.STRIPE_SECRET_KEY
            try:
                stripe_coupon = stripe.Coupon.retrieve(coupon.stripe_coupon_id)
                if stripe_coupon['valid'] == True:
                    messages.success(request, 'Coupon applied')
                else:
                    raise ValueError
            except:
                raise ValueError

            customer = get_customer_or_guest(request)
            order = Order.objects.get(
                customer=customer, complete=False)
            order.coupon = coupon
            order.save()
        except Coupon.DoesNotExist:
            messages.error(request, 'Coupon does not exist')
        except ValueError:
            messages.error(request, 'Coupon cannot be verified')
    else:
        messages.error(request, 'Coupon code is invalid')
    return redirect('order:checkout')


@require_POST
def coupon_remove(request):
    """
    remove coupon from the cart
    """
    if request.method == "POST":

        customer = get_customer_or_guest(request)
        order = Order.objects.get(
            customer=customer, complete=False)
        order.coupon = None
        order.save()
    return redirect('order:checkout')


def checkout(request):
    """Checkout view"""

    # pass stripe publishable key for checkout session
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    # to catch a case when user visits checkout page without visiting main page
    try:
        customer = get_customer_or_guest(request)
    except:
        return redirect('store:products')
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
        # redirect to the main page if there are not items in the cart
        if order.get_cart_items < 1:
            return redirect("store:products")
    else:
        # redirect to main page if there are not oustanding orders
        return redirect("store:products")
    return render(request, 'order/checkout.html', context=context)


@require_POST
def cash_checkout(request, pk):
    """
    Finalizing order with deferred payment - Cash payment
    """

    errors = []

    def catch_validation_errors(e):
        """
        Collect errors and return Unprocessable Entity HTTP response
        """
        for key, value in e:
            validation_error = key.upper() + " " + value[0]
            errors.append(validation_error)

    order = get_object_or_404(Order, transaction_id=pk)
    order.payment_method = "cash"
    # load data from POST to check delivery method
    try:
        data = json.loads(request.body)
    except:
        return HttpResponseNotFound()

    delivery = data.pop("delivery")

    # pop email and phone
    phone = data.pop('phone')
    email = data.pop('email')

    if delivery:
        order.delivery_method = "delivery"
        try:
            # manually trigger fields validation without saving a model
            ShippingAddress(**data).full_clean()
            # get or create Shipping Address (already saves data)
            shipping_address, created = ShippingAddress.objects.get_or_create(
                **data)
            # update shipping in order
            order.shipping = shipping_address
        except Exception as e:
            catch_validation_errors(e)
    else:
        order.delivery_method = "carryout"
        try:
            if data['urgency'] == 'custom':
                # change data format and make naive datetime object timezone aware
                data['pickup_date'] = make_aware(datetime.datetime.strptime(
                    data['pickup_date'], '%Y-%m-%d %I:%M %p'))
            elif data['urgency'] == 'asap':
                # for asap pick up date use today's date
                data['pickup_date'] = timezone.now().replace(
                    hour=0, minute=0, second=0, microsecond=0)
            # validate PickUp details
            PickUpDetail(**data).full_clean()
            # get or create PickUpDetail (already saves data)
            pickup_details, created = PickUpDetail.objects.get_or_create(
                **data)
            order.pickup = pickup_details
        # if wrong pickup_date passed for custom order
        except ValueError:
            errors.append('wrong pick up date format')
        # if no pickup_date passed for custom order
        except KeyError:
            errors.append('no pick up date passed')
        except Exception as e:  # to catch errors in PickUpDetail Form
            catch_validation_errors(e)

    # add email and phone to the order, and validate final form
    order.email = email
    order.phone = phone
    order.complete = True
    try:
        order.full_clean()
    except Exception as e:
        catch_validation_errors(e)

    # if errors are caught, return Unprocessable Entity Response
    if len(errors) > 0:
        return JsonResponse({"errors": errors}, status=422)

    # save order to apply payment and delivery methods
    order.save()
    return redirect(request.build_absolute_uri(reverse('order:success'))+"?cash=true")


@require_POST
def create_checkout_session(request, pk):
    """
    Stripe payment gateway for Online payment checkout
    Sessions are used to store ShippingAddress or PickUpDetails info
    """
    errors = []

    def catch_validation_errors(e):
        """
        Collect errors and return Unprocessable Entity HTTP response
        """
        for key, value in e:
            validation_error = key.upper() + " " + value[0]
            errors.append(validation_error)

    # get order by transaction_id
    order = get_object_or_404(Order, transaction_id=pk)
    # change order payment method to Online
    order.payment_method = "online"

    # load data from body/return 404 if no data
    try:
        data = json.loads(request.body)
    except:
        return HttpResponseNotFound()

    # get delivery status
    delivery = data.pop("delivery")
    # pop email and phone
    phone = data.pop('phone')
    email = data.pop('email')

    if delivery:
        order.delivery_method = "delivery"
        try:
            # validate data
            ShippingAddress(**data).full_clean()
            # save data in session - will be adjusted after payment is complete
            for key, value in data.items():
                request.session[key] = value
        except Exception as e:
            catch_validation_errors(e)
    else:
        order.delivery_method = "carryout"
        # validate data without pickup_date to avoid problems
        # with storing datetime object in Sessions
        data_to_validate = data.copy()
        data_to_validate.pop('pickup_date', None)
        try:
            # validate PickUp details
            PickUpDetail(**data_to_validate).full_clean()
            # save Pick-up data in session
            for key, value in data.items():
                request.session[key] = value
        except Exception as e:
            catch_validation_errors(e)

    # add email and phone to the order, and validate final form
    order.email = email
    order.phone = phone

    try:
        order.full_clean()
    except Exception as e:
        catch_validation_errors(e)

    # save order to apply payment and delivery methods
    order.save()

    # if errors are caught, return Unprocessable Entity Response
    if len(errors) > 0:
        return JsonResponse({"errors": errors}, status=422)

    # check if order has coupon and pass it to Stripe Payment Gateway
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

    stripe.api_key = settings.STRIPE_SECRET_KEY
    # Create Stripe Checkout Session
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=email,
            payment_method_types=['card'],
            line_items=line_items,
            discounts=[{
                'coupon': coupon_id,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('order:success'))+"?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(
                reverse('order:failed')),
        )
    except:
        return HttpResponseNotFound()
    # set session key to be checked when accessing Success Payment View
    request.session['redirected'] = True

    return JsonResponse({'sessionId': checkout_session.id})


class PaymentSuccessView(TemplateView):
    template_name = 'order/payment_success.html'

    def get(self, request, *args, **kwargs):
        # to capture the case of getting redirect from cash checkout as sessions are not saved
        referring_url = request.META.get('HTTP_REFERER', '')
        if 'checkout' in referring_url:  # check if redirected from cash checkout
            pass
        elif 'redirected' in request.session:  # check if redirected from stripe checkout
            del request.session['redirected']
        else:
            return HttpResponseNotFound()

        if not request.GET.get('cash'):
            session_id = request.GET.get('session_id')
            if session_id is None:
                return HttpResponseNotFound()

            customer = get_customer_or_guest(request)
            # order query set
            order_qs = Order.objects.filter(
                customer=customer, complete=False)
            # if order exists, get order instance
            if order_qs.exists():
                order = order_qs[0]

            # save shipping/carryout models
            if order.delivery_method == "delivery":
                # get model's field names
                shipping_list = [
                    field.name for field in ShippingAddress()._meta.get_fields()]
                # create shipping dictionary for model creation from session keys
                shipping_dict = {}
                for key in shipping_list:
                    shipping_dict[key] = request.session.get(key)
                # delete None values from dictionary
                shipping_dict = {k: v for k,
                                 v in shipping_dict.items() if v != None}
                # get create instance of shipping model
                shipping_address, created = ShippingAddress.objects.get_or_create(
                    **shipping_dict)
                order.shipping = shipping_address

            elif order.delivery_method == "carryout":
                # get model's field names
                carryout_list = [
                    field.name for field in PickUpDetail()._meta.get_fields()]
                # create carryout dictionary for model creation from session keys
                carryout_dict = {}
                for key in carryout_list:
                    carryout_dict[key] = request.session.get(key)
                # delete None values from dictionary
                carryout_dict = {k: v for k,
                                 v in carryout_dict.items() if v != None}

                # change data format and make naive datetime object timezone aware
                if carryout_dict['urgency'] == "custom":
                    carryout_dict['pickup_date'] = make_aware(datetime.datetime.strptime(
                        carryout_dict['pickup_date'], '%Y-%m-%d %I:%M %p'))
                else:
                    # for asap pick up date use today's date
                    carryout_dict['pickup_date'] = timezone.now().replace(
                        hour=0, minute=0, second=0, microsecond=0)

                # get or create instance of the pickup model
                carryout, created = PickUpDetail.objects.get_or_create(
                    **carryout_dict)
                try:
                    carryout.full_clean()
                except:
                    return JsonResponse({"errors": "Could not validate PickUpDetail"}, status=422)
                order.pickup = carryout
            else:
                return HttpResponseNotFound()

            order.paid = True
            order.complete = True
            order.save()
        return render(request, self.template_name)


class PaymentFailedView(TemplateView):
    template_name = 'order/payment_failed.html'

    def get(self, request, *args, **kwargs):
        """
        Check that 'redirected' session variable is set in api_checkout_view
        to avoid direct url access
        """
        if 'redirected' in request.session:
            del request.session['redirected']
        else:
            return HttpResponseNotFound()
        return render(request, self.template_name)
