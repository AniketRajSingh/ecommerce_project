from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    primary_phone_number = models.CharField(max_length=15)
    alternative_phone_number = models.CharField(max_length=15)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    
    # Permanent Address Fields
    permanent_street = models.CharField(max_length=255, blank=True, null=True)
    permanent_city = models.CharField(max_length=100, blank=True, null=True)
    permanent_state = models.CharField(max_length=100, blank=True, null=True)
    permanent_pincode = models.CharField(max_length=20, blank=True, null=True)
    permanent_landmark = models.CharField(max_length=255, blank=True, null=True)
    
    # Shipping Address Fields
    shipping_street = models.CharField(max_length=255, blank=True, null=True)
    shipping_city = models.CharField(max_length=100, blank=True, null=True)
    shipping_state = models.CharField(max_length=100, blank=True, null=True)
    shipping_pincode = models.CharField(max_length=20, blank=True, null=True)
    shipping_landmark = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username
