from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.http import HttpResponse
from .models import Account
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
import requests

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from carts.utils import _cartid

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                email = email,
                username = username,
                password = password
            )
            user.phone_number = phone_number
            user.save()

            # User Activation logic
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account!'
            message = render_to_string('accounts/account_verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': default_token_generator.make_token(user)
            })
            to_mail = form.cleaned_data['email']
            send_email = EmailMessage(mail_subject, message, to=[to_mail])
            send_email.send()
    
            url = '/accounts/login/?command=verification&email='+ email
            return redirect(url)
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cartid(request))
                cart_item_exists = CartItem.objects.filter(cart=cart).exists()

                # 
                if cart_item_exists:
                    cart_items = CartItem.objects.filter(cart=cart)

                    # Getting the product variations by cart id
                    product_variation = []
                    for item in cart_items:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the cart items from the user to access his product variations
                    cart_items = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id_list = []

                    for item in cart_items:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id_list.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id_list[index]

                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()

                        else:
                            cart_items = CartItem.objects.filter(cart=cart)
                            for item in cart_items:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in!')
            url = request.META.get('HTTP_REFERER')
            try:
                # Extracting the query string: "next=/cart/checkout/"
                query = requests.utils.urlparse(url).query

                # convert the string into Python Dictionary
                params = dict(x.split('=') for x in query.split('&'))
                # Check if 'next' exists in the dictionary
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)

            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials!')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out!')
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congtratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Inavlid activation link!')
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']

        if Account.objects.filter(email__exact=email).exists():
            user = Account.objects.get(email__exact=email)

            # Forgot Password validation Link
            current_site = get_current_site(request)
            mail_subject = 'Please Reset Your Password!'
            message = render_to_string('accounts/reset_password_email.html', {
                'user':user,
                'domain':current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.id)),
                'token': default_token_generator.make_token(user),
            })
            to_mail = email
            send_email = EmailMessage(mail_subject, message, to=[to_mail])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')

        else:
            messages.error(request, 'Email does not exists!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetPassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    
    else:
        messages.error(request, 'This link has been expired.')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)

            user.set_password(password)
            user.save()

            messages.success(request, 'Password reset successfull!')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    return render(request, 'accounts/resetPassword.html')