from order.models import Order
from users.models import Customer

# to display number of items in the cart in the Navbar of the base.html


def get_cart_quantity(request):
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
        except:
            number_of_items = 0
    else:
        try:
            # create customer assigning device cookie
            customer, created = Customer.objects.get_or_create(
                device=request.COOKIES['device'])
        except:
            return {
                'cart_quantity': 0
            }
    try:
        customer_order = Order.objects.filter(
            customer=customer, complete=False)[0]
        number_of_items = customer_order.get_cart_items
    except:
        number_of_items = 0
    finally:
        return {
            'cart_quantity': number_of_items
        }
