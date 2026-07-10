from django.shortcuts import render
from store.models import Product
from site_settings.models import HomepageBanner

def home(request):
    banner = HomepageBanner.objects.all().filter(is_active=True).first()
    products = Product.objects.all().filter(is_available=True)
    context = {
        'products':products,
        'banner':banner,
    }
    return render(request, 'home.html', context)