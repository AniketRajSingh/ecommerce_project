from django.urls import path
from .views import order_confirmation, place_order, product_list, product_detail, add_to_cart,remove_cart_item, cart,customer_support,substract_from_cart

urlpatterns = [
   
    path('products/', product_list, name='product_list'),
    path('products/<int:product_id>/', product_detail, name='product_detail'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('substract_from_cart/<int:product_id>/', substract_from_cart, name='substract_from_cart'),
    path('remove_cart_item/<int:product_id>/', remove_cart_item, name='remove_cart_item'),
    path('cart/', cart, name='cart'),
    path('CustomerSupport/', customer_support, name='customer_support'),
    path('order-confirmation/', order_confirmation, name='order_confirmation'),
    path('place-order/', place_order, name='place_order'),
    
]
