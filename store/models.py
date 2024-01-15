from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Quantity(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Media(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    media_url = models.URLField(max_length=200)

    def __str__(self):
        return f"{self.product.name} - {self.get_media_type_display()}"

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantities = models.ManyToManyField(Quantity, through='ProductQuantity')
    description = models.TextField()
    short_description = models.TextField()

    def __str__(self):
        return self.name

class ProductQuantity(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.ForeignKey(Quantity, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} - {self.product}"

class Order(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Out For Delivery', 'Out For Delivery'),
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

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.ForeignKey(Quantity, on_delete=models.CASCADE)
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
