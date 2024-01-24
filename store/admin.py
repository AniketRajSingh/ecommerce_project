from django.contrib import admin
from .models import Category, Quantity, Product, Order, OrderItem, ProductQuantity, Media, Cancellation

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


class CancellationInline(admin.StackedInline):
    model = Cancellation
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline, CancellationInline]
    list_display = ('id', 'user', 'delivery_status', 'total_price', 'created_at')

    def cancellation_reason(self, obj):
        # Display the cancellation reason if the order is cancelled
        cancellation = Cancellation.objects.filter(order=obj).first()
        return cancellation.reason if cancellation else '-'


admin.site.register(Order, OrderAdmin)
