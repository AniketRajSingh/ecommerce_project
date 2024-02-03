from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

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
    categories = models.ManyToManyField(Category)
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
        ('Return Requested', 'Return Requested'),
        ('Return Accepted', 'Return Accepted'),
        ('Return Rejected', 'Return Rejected'),
        ('Returned', 'Returned'),
        ('Refunded', 'Refunded'),
        ('Replacement Required', 'Replacement Required'),
        ('Replacement Accepted', 'Replacement Accepted'),
        ('Replacement Rejected', 'Replacement Rejected'),
        ('Product Replaced', 'Product Replaced'),
        ('Replacement Complete', 'Replacement Complete'),
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
    permanent_street = models.TextField()
    permanent_city = models.TextField()
    permanent_state = models.TextField()
    permanent_pincode = models.TextField()
    permanent_landmark = models.TextField()
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
    item_quantity = models.DecimalField(max_digits=3, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item_quantity} x {self.product.name} {self.quantity} in Order {self.order.id}"

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

class SalesData(models.Model):
    date = models.DateField(default=date.today)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"SalesData - {self.date}"
    
@receiver(post_save, sender=Order)
def update_sales_data(sender, instance, created, **kwargs):
    if created:
        # Get or create SalesData for the current date
        sales_data, created = SalesData.objects.get_or_create(date=date.today())
        # Update total sales based on the new order
        sales_data.total_sales += instance.total_price
        sales_data.save()