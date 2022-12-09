from order.models import Order, OrderItem


# to display number of items in the cart in the Navbar of the base.html

def get_cart_quantity(request):
    try:
        customer_order = Order.objects.filter(
            customer=request.user, complete=False)[0]
        number_of_items = customer_order.get_cart_items
    except:
        number_of_items = 0
    finally:
        return {
            'cart_quantity': number_of_items
        }
