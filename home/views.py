from django.shortcuts import render
from store.models import Product, Category
from django import forms
from django.http import HttpResponse
from .models import HomePagePopup , Review, HomePageCarousel

from django.shortcuts import render

def home(request):
    # Fetch recommended products, special offers, and reviews
    products = Product.objects.all()
    recommended_products = list(Product.objects.all().order_by('?')[:4])
    carousel_url = HomePageCarousel.objects.all()
    
    special_offers_category = Category.objects.get(name='Special Offers')
    special_offers_products = Product.objects.filter(categories=special_offers_category).order_by('?')[:4]

    chunk_size = 4

    # Pad the products list with None to make it a multiple of chunk_size
    total_products = len(products)
    padding = (chunk_size - total_products % chunk_size) % chunk_size
    padded_products = list(products) + [None] * padding

    # Create chunks of size chunk_size
    product_chunks = [padded_products[i:i + chunk_size] for i in range(0, len(padded_products), chunk_size)]

    reviews = Review.objects.all()  # Fetch the latest 3 reviews

    popup_content = HomePagePopup.objects.first()

    return render(request, 'index.html', {
        'special_offers_products': special_offers_products,
        'recommended_products': recommended_products,
        'reviews': reviews,
        'popup_content': popup_content,
        'carousel_url': carousel_url,
        'product_chunk_list': product_chunks
    })

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