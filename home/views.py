from django.shortcuts import render
from store.models import Product, Category
from django import forms
from django.http import HttpResponse
from .models import HomePagePopup , Review

def home(request):
    # Fetch recommended products, special offers, and reviews
    products = Product.objects.all().order_by('?')[:4]
    recommended_products = list(products)
    
    special_offers_category = Category.objects.get(name='Special Offers')
    special_offers_products = Product.objects.filter(categories=special_offers_category).order_by('?')[:3]

    reviews = Review.objects.all()[:3]  # Fetch the latest 3 reviews

    popup_content = HomePagePopup.objects.first()

    return render(request, 'index.html', {'special_offers_products': special_offers_products,
                                           'recommended_products': recommended_products,
                                           'reviews': reviews,
                                           'popup_content': popup_content})

def product_search(request):
    query = request.GET.get('q', '') 
    products = Product.objects.filter(name__icontains=query)  

    return render(request, 'store/search_results.html', {'products': products, 'query': query})

def about(request):  
    return render(request, 'about.html')

def contact(request):  
    return render(request, 'contact.html')

def handler404(request, template_name="404.html"):
    response = render(request, template_name)
    response.status_code = 404
    return response

class ContactForm(forms.Form):
    name = forms.CharField(label='Your Name', max_length=100)
    email = forms.EmailField(label='Your Email')
    message = forms.CharField(label='Your Message', widget=forms.Textarea)

def contact_view(request):
    form = ContactForm()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            return render(request, 'contact.html', {'form': form})

    return render(request, 'contact.html', {'form': form})

def health_check(request):
    return HttpResponse("OK")