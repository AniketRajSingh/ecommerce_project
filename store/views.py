# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Product, Order, Category
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .razorpay_utils import create_order, verify_payment

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
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1

    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({'success': True, 'cart': cart})

@require_POST
def substract_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str] -= 1
        if cart[product_id_str] <= 0:
            del cart[product_id_str]
    else:
        cart[product_id_str] = 0

    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({'success': True, 'cart': cart})

@require_POST
def remove_cart_item(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]

    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({'success': True, 'cart': cart})

def cart(request):
    cart = request.session.get('cart', {})

    if not cart:
        return render(request, 'store/cart.html', {'products_in_cart': [], 'total_price': 0})

    product_ids_in_cart = cart.keys()
    products_in_cart = Product.objects.filter(id__in=product_ids_in_cart)
    total_prices = calculate_total_prices(products_in_cart)

    return render(request, 'store/cart.html', {'products_in_cart': products_in_cart, 'total_prices': total_prices, 'cart': cart})

def customer_support(request):
    return render(request, 'store/customer_support.html')

def order_confirmation(request):
    cart = request.session.get('cart', {})
    product_ids_in_cart = cart.keys()
    products_in_cart = Product.objects.filter(id__in=product_ids_in_cart)
    total_prices = calculate_total_prices(products_in_cart, cart)

    return render(request, 'store/order_confirmation.html', {'products_in_cart': products_in_cart, 'total_prices': total_prices, 'cart': cart, 'razorpay_key': 'rzp_test_esc8vkRRLTMjAN'})

@login_required
def place_order(request):
    if request.method == 'POST':
        # Validate the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')

        cart = request.session.get('cart', {})
        product_ids_in_cart = cart.keys()
        products_in_cart = Product.objects.filter(id__in=product_ids_in_cart)
        total_prices = calculate_total_prices(products_in_cart, cart)

        # Create an order for the authenticated user
        order = Order.objects.create(
            user=request.user,
            name=name,
            email=email,
            phone=phone,
            address=address,
        )

        # Add ordered products to the order
        for product_id, quantity in request.session.get('cart', {}).items():
            product = Product.objects.get(id=product_id)
            order.order_items.create(
                product=product,
                quantity=quantity,
                price=product.final_price,
            )

        order.total_price = sum(total_prices[product_id][quantity_id]['final_price'] * cart[product_id] for product_id, quantity_id in cart.items())

        # Initiate payment with the order amount and get Razorpay order ID
        razorpay_order_id = create_order(order.total_price, order.id)
        payment_id = razorpay_payment_id
        r_order_id = razorpay_order_id['id']

        if verify_payment(payment_id, order.total_price, order.id,r_order_id):
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
