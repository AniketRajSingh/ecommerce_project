from django.db import models

# Create your models here.

class HomePagePopup(models.Model):
    image_url = models.URLField()
    description = models.TextField()
    button_name = models.CharField(max_length=255)
    redirection_link = models.URLField()

    def __str__(self):
        return self.description