from django.contrib import admin
from .models import Review, HomePagePopup, HomePageCarousel
from django import forms
from django.forms.widgets import RadioSelect

class HomePagePopupAdminForm(forms.ModelForm):
    class Meta:
        model = HomePagePopup
        fields = [ 'name', 'image_url', 'description', 'button_name', 'redirection_link', 'display_on_homepage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instances = kwargs.get('instance', None)
        if instances:
            # If there is an existing instance, set the display_on_homepage
            # field to False for all instances except the current one.
            for instance in HomePagePopup.objects.all():
                if instance != instances:
                    instance.display_on_homepage = False
                    instance.save()

        self.fields['display_on_homepage'] = forms.ChoiceField(
            choices=[(True, 'Display on homepage'), (False, 'Do not display on homepage')],
            widget=RadioSelect,
            initial=False,
        )

class HomePagePopupAdmin(admin.ModelAdmin):
    form = HomePagePopupAdminForm


admin.site.register(HomePagePopup, HomePagePopupAdmin)
admin.site.register(HomePageCarousel)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'location', 'review_text', 'photo_url')

