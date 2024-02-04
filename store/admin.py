from django.contrib import admin
from .models import Category, Quantity, Product, Order, OrderItem, ProductQuantity, Media, Cancellation, SalesData
from django.db.models.functions import TruncDate
from django.db.models import Sum, Count

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
        cancellation = Cancellation.objects.filter(order=obj).first()
        return cancellation.reason if cancellation else '-'

admin.site.register(Order, OrderAdmin)

class SalesDataAdmin(admin.ModelAdmin):
    change_list_template = 'admin/sales_data_change_list.html'

    def changelist_view(self, request, extra_context=None):
        # Logic to get data for Sales Chart
        aggregated_data = SalesData.objects.annotate(chart_date=TruncDate('date')).values('chart_date').annotate(revenue=Sum('total_sales')).order_by('chart_date')
        chart_data = list(aggregated_data)
        for entry in chart_data:
            entry['chart_date'] = entry['chart_date'].isoformat()
            entry['revenue'] = float(entry['revenue'])

        # Logic to get data for Product Quantity chart
        product_quantity_data = OrderItem.objects.values('product__name').annotate(total_quantity=Sum('item_quantity'))

        product_quantity_chart_data = list(product_quantity_data)
        for entry in product_quantity_chart_data:
            entry['product_name'] = entry['product__name']
            entry['total_quantity'] = float(entry['total_quantity'])

        # Logic to get data for Order Status chart
        order_status_data = Order.objects.values('delivery_status').annotate(total_orders=Count('id'))

        order_status_chart_data = list(order_status_data)
        for entry in order_status_chart_data:
            entry['delivery_status'] = entry['delivery_status']
            entry['total_orders'] = float(entry['total_orders'])

        extra_context = extra_context or {}
        extra_context['chart_data'] = chart_data
        extra_context['product_quantity_data'] = product_quantity_chart_data
        extra_context['order_status_data'] = order_status_chart_data
        print('chart data',chart_data,'\n')
        print('product quantity data',product_quantity_chart_data,'\n')
        print('Order Status data',order_status_chart_data)

        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(SalesData, SalesDataAdmin)
