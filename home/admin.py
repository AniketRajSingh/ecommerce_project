from django.contrib import admin
from .models import HomePagePopup,Review
# Register your models here.
admin.site.register(HomePagePopup)
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'location', 'review_text', 'photo_url')