from django.urls import path
from .views import home, product_search,contact,about, health_check
from store.views import my_orders,cancel_order, return_order, replace_order

urlpatterns = [
    path('', home, name='home'),
    path('search/', product_search, name='product_search'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about'),
    path('my-orders/', my_orders, name='my_orders'),
    path('order/<int:order_id>/cancel/', cancel_order, name='cancel_order'),
    path('order/<int:order_id>/return/', return_order, name='return_order'),
    path('order/<int:order_id>/replace/', replace_order, name='replace_order'),
    path('health-check/', health_check, name='health_check'),
]
