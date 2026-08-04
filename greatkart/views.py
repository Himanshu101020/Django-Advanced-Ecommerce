from django.shortcuts import render
from store.models import Product, ReviewRating
from site_settings.models import HomepageBanner

def home(request):
    banner = HomepageBanner.objects.all().filter(is_active=True).first()
    products = Product.objects.all().filter(is_available=True).order_by('created_date')


    context = {
        'products':products,
        'banner':banner,
    }
    return render(request, 'home.html', context)