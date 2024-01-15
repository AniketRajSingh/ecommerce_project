from django.contrib import admin
from .models import Category, Quantity, Product, Order, OrderItem, ProductQuantity, Media

admin.site.register(Category)
admin.site.register(Quantity)

class ProductQuantityInline(admin.TabularInline):
    model = Product.quantities.through
    extra = 1

class ProductQuantityAdmin(admin.ModelAdmin):
    model = ProductQuantity
    extra = 1

class MediaInline(admin.TabularInline):
    model = Media
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductQuantityInline, MediaInline]

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductQuantity, ProductQuantityAdmin)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)
