from django.shortcuts import render, redirect
from django.http import JsonResponse
from carts.models import CartItem
from orders.models import Order, OrderProduct, Payment
from store.models import Product
from .forms import OrderForm
import datetime
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store Transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status']
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to OrderProduct table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product.id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True

        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()

        # Reduce the quantity of sold products
        product = Product.objects.get(id=item.product.id)
        product.stock -= item.quantity
        product.save()


    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order received email to the customer
    mail_subject = "Thank you for your order!"
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order
    })

    to_email = request.user.email
    send_eamil = EmailMessage(mail_subject, message, to=[to_email])
    send_eamil.send()

    # Send order number and transaction id back to the sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id
    }
    
    return JsonResponse(data)

def place_order(request):
    total = 0
    tax = 0
    grand_total = 0
    
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect to store
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)

    tax = (2 * total)/100
    grand_total = total + tax
    
    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.country = form.cleaned_data['country']
            data.pincode = form.cleaned_data['pincode']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.order_note = form.cleaned_data['order_note']

            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')

            data.save()
            # Generating date string
            current_date = datetime.date.today().strftime("%Y%m%d")
            
            # Concatenate date + database id
            order_number = current_date + str(data.id)

            data.order_number = order_number
            data.save()

            # Fetch the pending orders
            order = Order.objects.get(
                user = current_user,
                is_ordered = False,
                order_number = order_number
            )
            context = {
                'order': order,
                'cart_items':cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total
            }

            return render(request, 'orders/payments.html', context)

def order_complete(request):
    order_number = request.GET.get('order_number')
    transaction_id = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        payment = Payment.objects.get(payment_id=transaction_id)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        sub_total = 0
        for op in ordered_products:
            sub_total += op.product_price * op.quantity
        context = {
            'order_number': order_number,
            'transID': transaction_id,
            'order':order,
            'payment':payment,
            'ordered_products':ordered_products,
            'sub_total':sub_total
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
