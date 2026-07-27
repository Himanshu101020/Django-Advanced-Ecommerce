from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Variation
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from .utils import get_cart_data, _cartid

# def _cartid(request):
#     cart = request.session.session_key
#     if not cart:
#         cart = request.session.create()
#     return cart

def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) # get the product

    # If the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(
                        product = product,
                        variation_category__iexact = key,
                        variation_value__iexact = value
                    )
                    product_variation.append(variation)
                except:
                    pass

        cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            id_list = []
            for item in cart_item:
                existing_variations = item.variations.all()
                ex_var_list.append(list(existing_variations))
                id_list.append(item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id_list[index]

                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(
                    product = product,
                    user = current_user,
                    quantity = 1
                )
                if len(product_variation)>0:
                    item.variations.add(*product_variation)
                item.save()
        else:
            item = CartItem.objects.create(
                product=product,
                user=current_user,
                quantity=1
            )
            if len(product_variation)>0:
                item.variations.add(*product_variation)
            item.save()

        return redirect('cart')

    # If user is not authenticated
    else:
        product_variation = []    
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]  
                try:
                    variation = Variation.objects.get(
                        product = product,
                        variation_category__iexact = key,
                        variation_value__iexact = value
                    )
                    product_variation.append(variation)

                except:
                    pass
        try:
            cart = Cart.objects.get(cart_id=_cartid(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cartid(request))
        cart.save()

        cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            ex_var_list = []
            id_list = []
            for item in cart_item:
                existing_variations = item.variations.all()
                ex_var_list.append(list(existing_variations))  
                id_list.append(item.id)
                

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id_list[index]

                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity +=1
                item.save()

            else:
                item = CartItem.objects.create(
                    product = product,
                    cart = cart,
                    quantity = 1
                )
                if len(product_variation)>0:
                    item.variations.add(*product_variation)
                
                item.save()

            
        else:
            item = CartItem.objects.create(
                product = product,
                cart = cart,
                quantity = 1
            )
            if len(product_variation)>0:
                item.variations.add(*product_variation)
            
            item.save()
        
        return redirect('cart')

def cart(request):
    context = get_cart_data(request)
    return render(request, 'store/cart.html', context)

# view logic for decrement button
def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cartid(request))
            cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cartid(request))
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)

    cart_item.delete()
    return redirect('cart')

@login_required(login_url='login')
def checkout(request):
    context = get_cart_data(request)
    return render(request, 'store/checkout.html', context)