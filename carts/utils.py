from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from carts.models import Cart, CartItem


def _cartid(request):
    """
    Helper function to get or create the session cart ID
    """
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def get_cart_data(request):
    """
    Helper function to calculate cart totals globally
    Returns a dictionary of context data
    """
    total=0
    quantity=0
    cart_items=None
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cartid(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

     # Return the packaged data as a dictionary
    return {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
