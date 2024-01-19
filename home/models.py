from django.db import models

# Create your models here.

class HomePagePopup(models.Model):
    image_url = models.URLField()
    description = models.TextField()
    button_name = models.CharField(max_length=255)
    redirection_link = models.URLField()

    def __str__(self):
        return self.description

class Review(models.Model):
    customer_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)  # Add a field for the customer's location
    review_text = models.TextField()
    photo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.customer_name}'s Review from {self.location}"
