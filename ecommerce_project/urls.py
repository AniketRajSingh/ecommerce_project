"""ecommerce_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "SNEH-SATTVA Admin"
admin.site.site_title = "SNEH-SATTVA Admin Portal"
admin.site.index_title = "Welcome to the SNEH-SATTVA's Admin Page"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('store/', include('store.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin-interface/logo/22222.jpg', RedirectView.as_view(url='/static/admin-interface/logo/22222.jpg')),
    path('admin-interface/favicon/22222.jpg', RedirectView.as_view(url='/static/admin-interface/favicon/22222.jpg')),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
