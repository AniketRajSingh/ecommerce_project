from django.db import models

class HomePagePopup(models.Model):
    name = models.CharField(max_length=255)
    image_url = models.FileField(upload_to='popup_images/')
    description = models.TextField()
    button_name = models.CharField(max_length=255)
    redirection_link = models.URLField()
    display_on_homepage = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Review(models.Model):
    customer_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)  # Field added for the customer's location
    review_text = models.TextField()
    photo_url = models.FileField(upload_to='review_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.customer_name}'s Review from {self.location}"

class HomePage(models.Model):
    selected_popup = models.ForeignKey(HomePagePopup, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return "Home Page"

class HomePageCarousel(models.Model):
    MEDIA_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    media_type = models.CharField(max_length=10, choices=MEDIA_CHOICES, default='image')
    media_url = models.FileField(upload_to='homepagecarousel/')
    image_description = models.TextField()

    def __str__(self):
        return self.image_description
