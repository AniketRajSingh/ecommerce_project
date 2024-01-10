from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    img = models.URLField(max_length=200)
    description = models.TextField()
    available = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class OrderStatus(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
        ('Replaced', 'Replaced'),
    ]

    delivery_status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS_CHOICES,
        default='Pending',
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=255, blank=True, null=True)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.CharField(max_length=20, blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_timestamp = models.DateTimeField(blank=True, null=True)
    status = models.ForeignKey(OrderStatus, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

class Cancellation(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    reason = models.TextField()
    date_requested = models.DateTimeField(auto_now_add=True)

class Return(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    reason = models.TextField()
    date_requested = models.DateTimeField(auto_now_add=True)

class Replacement(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    reason = models.TextField()
    date_requested = models.DateTimeField(auto_now_add=True)