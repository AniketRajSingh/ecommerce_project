# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Product, Order, Category, Quantity
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .razorpay_utils import create_order, verify_payment
from django.db.models import F, ExpressionWrapper, fields, Sum

def product_list(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')

    if selected_category:
        products = Product.objects.filter(categories__name=selected_category)
    else:
        products = Product.objects.all()

    selected_quantities = {}

    for product in products:
        product_quantities = product.productquantity_set.all()

        for quantity_instance in product_quantities:
            if quantity_instance.available:
                selected_quantities[product.id] = quantity_instance.quantity.id
                break

    total_prices = calculate_total_prices(products)

    return render(request, 'store/product_list.html', {'products': products, 'total_prices': total_prices, 'categories': categories, 'selected_category': selected_category, 'selected_quantities': selected_quantities})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Retrieve product quantities for rendering buying options
    product_quantities = product.productquantity_set.all()
    for quantity_instance in product_quantities:
        if quantity_instance.available:
            initial_quantity_id = quantity_instance.quantity.id
            break

    return render(request, 'store/product_detail.html', {
        'product': product,
        'product_quantities': product_quantities,
        'selected_quantity': initial_quantity_id,
    })

@require_POST
def add_to_cart(request, product_id, quantity_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    quantity_id_str = str(quantity_id)
    
    # Ensure the quantity is valid for the product
    product = get_object_or_404(Product, id=product_id)
    quantity = get_object_or_404(Quantity, id=quantity_id)

    key = f"{product_id_str}-{quantity_id_str}"

    if key in cart:
        cart[key]['quantity'] += 1
    else:
        cart[key] = {'quantity_id': quantity_id, 'quantity': 1}

    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({'success': True, 'cart': cart})

@require_POST
def substract_from_cart(request, product_id, quantity_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    quantity_id_str = str(quantity_id)
    key = f"{product_id_str}-{quantity_id_str}"

    if key in cart:
        cart[key]['quantity'] -= 1
        if cart[key]['quantity'] <= 0:
            del cart[key]
    else:
        cart[key] = {'quantity_id': quantity_id, 'quantity': 0}

    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({'success': True, 'cart': cart})

@require_POST
def remove_cart_item(request, product_id, quantity_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    quantity_id_str = str(quantity_id)
    key = f"{product_id_str}-{quantity_id_str}"

    if key in cart:
        del cart[key]

    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({'success': True, 'cart': cart})


def cart(request):
    cart = request.session.get('cart', {})

    if not cart:
        return render(request, 'store/cart.html', {'cart_data': {}})

    product_data_dict = {}
    total_items = 0  # Add this variable to track the total number of items in the cart

    for item, quantity_data in cart.items():
        # Check if the item follows the expected format
        if '-' in item:
            product_id, quantity_id = map(int, item.split('-'))
            quantity = quantity_data.get('quantity', 0)
            total_items += quantity  # Increment total_items by the quantity

            # Fetch product details
            product = Product.objects.get(id=product_id)
            quantity_instance = Quantity.objects.get(id=quantity_id)
            price = product.productquantity_set.get(quantity=quantity_instance).price
            final_price = product.productquantity_set.get(quantity=quantity_instance).final_price

            # Create or update product data in the dictionary
            if product_id not in product_data_dict:
                product_data_dict[product_id] = {
                    'product_id': product_id,
                    'name': product.name,
                    'image_urls': [media.media_url for media in product.media_set.filter(media_type='image')],
                    'quantities': {},
                }

            product_data_dict[product_id]['quantities'][quantity_id] = {
                'price': price,
                'final_price': final_price,
                'quantity': quantity,
                'quantity_instance': quantity_instance,
            }

    total_price = sum(
        quantity_data['quantity'] * quantity_data['final_price']
        for product_id, product_data in product_data_dict.items()
        for quantity_id, quantity_data in product_data['quantities'].items()
    )

    context = {
        'cart_data': {
            'total_price': total_price,
            'total_items': total_items,
            'products': product_data_dict.values(),
        },
    }

    return render(request, 'store/cart.html', context)

def customer_support(request):
    return render(request, 'store/customer_support.html')

def order_confirmation(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, 'Your cart is empty. Add items to your cart before proceeding.')
        return redirect('cart')

    product_data_dict = {}

    for item, quantity_data in cart.items():
        # Check if the item follows the expected format
        if '-' in item:
            product_id, quantity_id = map(int, item.split('-'))
            quantity = quantity_data.get('quantity', 0)
            
            # Fetch product details
            product = Product.objects.get(id=product_id)
            quantity_instance = Quantity.objects.get(id=quantity_id)
            price = product.productquantity_set.get(quantity=quantity_instance).price
            final_price = product.productquantity_set.get(quantity=quantity_instance).final_price
            
            # Create or update product data in the dictionary
            if product_id not in product_data_dict:
                product_data_dict[product_id] = {
                    'product_id': product_id,
                    'name': product.name,
                    'image_urls': [media.media_url for media in product.media_set.filter(media_type='image')],
                    'quantities': {},
                }
            
            product_data_dict[product_id]['quantities'][quantity_id] = {
                'price': price,
                'final_price': final_price,
                'quantity': quantity,
                'quantity_instance':quantity_instance,
            }

    total_price = sum(
        quantity_data['quantity'] * quantity_data['final_price']
        for product_id, product_data in product_data_dict.items()
        for quantity_id, quantity_data in product_data['quantities'].items()
    )

    context = {
        'product_data': product_data_dict.values(),
        'total_price': total_price,
        'cart': cart,
        'razorpay_key': 'rzp_test_esc8vkRRLTMjAN',
    }

    return render(request, 'store/order_confirmation.html', context)

@login_required
def place_order(request):
    # Retrieve cart details
    cart = request.session.get('cart', {})
    if request.method == 'POST' and cart:
        # Validate the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # Retrieve Razorpay payment details
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')


        # Create an order for the authenticated user
        order = Order.objects.create(
            user=request.user,
            name=name,
            email=email,
            phone=phone,
            address=address,
        )

        # Add ordered products to the order
        for key, quantity_data in cart.items():
            # Split the key into product_id and quantity_id
            product_id_str, quantity_id_str = key.split('-')
            product_id = int(product_id_str)
            quantity_id = int(quantity_id_str)

            product = Product.objects.get(id=product_id)
            quantity = Quantity.objects.get(id=quantity_id)

            order.order_items.create(
                product=product,
                quantity=quantity,
                item_quantity=quantity_data['quantity'],
                price=product.productquantity_set.get(quantity=quantity).final_price,
            )

        order.total_price = order.order_items.aggregate(
            total_price=Sum(F('price') * F('item_quantity'))
        )['total_price'] or 0

        # Initiate payment with the order amount and get Razorpay order ID
        razorpay_order_id = create_order(order.total_price, order.id)
        payment_id = razorpay_payment_id
        r_order_id = razorpay_order_id['id']

        if verify_payment(payment_id, order.total_price, order.id, r_order_id):
            # Clear the cart
            request.session['cart'] = {}

            # Pass Razorpay order ID to the template
            return render(request, 'store/order_placed.html', {'order': order, 'razorpay_order_id': razorpay_order_id})

        # If payment verification fails, delete the order, display an error message, and redirect to order confirmation
        order.delete()
        messages.error(request, 'Payment verification failed. Please try again.')
        return redirect('order_confirmation')

    # Redirect to the order confirmation page if the form is not submitted via POST
    return redirect('order_confirmation')

def calculate_total_prices(products):
    total_prices = {}

    for product in products:
        total_prices[product.id] = {}
        for product_quantity in product.productquantity_set.filter(quantity__in=product.quantities.all()):
            total_prices[product.id][product_quantity.quantity.id] = {
                'price': product_quantity.price,
                'final_price': product_quantity.final_price,
                'available': product_quantity.available,
            }

    return total_prices


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})

def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.delivery_status == 'Pending':
        # Implement cancellation logic (e.g., update order status)
        order.delivery_status = 'Cancelled'
        order.save()

        messages.success(request, 'Order cancelled successfully.')
    else:
        messages.error(request, 'Cannot cancel order. Delivery status is not pending.')

    return redirect('my_orders')

def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.delivery_status == 'Delivered':
        # Implement return logic (e.g., update order status)
        order.delivery_status = 'Returned'
        order.save()

        messages.success(request, 'Order returned successfully.')
    else:
        messages.error(request, 'Cannot return order. Delivery status is not delivered.')

    return redirect('my_orders')

def replace_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.delivery_status == 'Delivered':
        # Implement replacement logic (e.g., update order status)
        order.delivery_status = 'Replaced'
        order.save()

        messages.success(request, 'Order replaced successfully.')
    else:
        messages.error(request, 'Cannot replace order. Delivery status is not delivered.')

    return redirect('my_orders')
