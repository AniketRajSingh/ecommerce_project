from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    first_name = models.CharField(max_length=30)  
    last_name = models.CharField(max_length=30)  

    def __str__(self):
        return self.user.username
