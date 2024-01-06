import razorpay
from django.conf import settings
from django.utils import timezone
from .models import Order


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_order(amount, currency='INR'):
    # Create a Razorpay order
    total_price_in_paisa = int(amount * 100)
    order = razorpay_client.order.create({
        'amount': total_price_in_paisa,
        'currency': 'INR',
        'payment_capture': 1, 
    })

    return order

def verify_payment(payment_id, amount, order_id,razorpay_order_id):
    payment = razorpay_client.payment.fetch(payment_id)
    print("Payment Details:", payment)
    print(payment['amount'],amount)
    print(order_id)

    if payment['amount'] == amount*100:
        # Update the order with payment details
        order = Order.objects.get(id=order_id)
        order.total_price = amount
        order.payment_id = payment_id
        order.order_id = razorpay_order_id
        order.payment_status = payment['status']
        order.payment_amount = payment['amount'] / 100  # Convert from paisa to rupees
        order.payment_timestamp = timezone.datetime.fromtimestamp(payment['created_at'])

        order.save()

        return True
    else:
        return False
