from django.contrib import admin
from .models import Category, Quantity, Product, Order, OrderItem, ProductQuantity, Media, Cancellation, SalesData
from django.db.models.functions import TruncDate
from django.db.models import Sum, Count
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
import xlsxwriter

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
    date_hierarchy = 'date'
    actions = ['generate_excel_report']

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
        return super().changelist_view(request, extra_context=extra_context)

    def generate_excel_report(self, request, queryset):
        # Get data for Sales Chart
        chart_data = queryset.annotate(chart_date=TruncDate('date')).values('chart_date').annotate(revenue=Sum('total_sales')).order_by('chart_date')
        chart_data = list(chart_data)
        
        # Convert data to a DataFrame
        df_sales = pd.DataFrame(chart_data)
    
        # Ensure the 'Revenue' column is numeric
        df_sales['revenue'] = pd.to_numeric(df_sales['revenue'])
    
        # Create an Excel writer with the xlsxwriter engine
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df_sales.to_excel(writer, sheet_name='SalesData', index=False)
    
        # Access the xlsxwriter workbook and worksheet objects directly
        workbook  = writer.book
        worksheet = writer.sheets['SalesData']
    
        # Create a chart object
        sales_chart = workbook.add_chart({'type': 'line'})
    
        # Configure the chart with the series data
        sales_chart.add_series({'values': '=SalesData!$B$2:$B${}'.format(len(chart_data) + 1),
                                'name': 'Revenue'})
    
        # Configure the chart axes and title
        sales_chart.set_title({'name': 'Sales Chart'})
        sales_chart.set_x_axis({'name': 'Date'})
        sales_chart.set_y_axis({'name': 'Revenue'})
    
        # Insert the chart into the worksheet
        worksheet.insert_chart('D2', sales_chart)
    
        # Get the number format for the 'Revenue' column
        num_format = workbook.add_format({'num_format': '#,##0.00'})
        
        # Apply the number format to the 'Revenue' column
        worksheet.set_column('C:C', None, num_format)
    
        # Save the Excel file
        writer.close()
    
        # Create an HTTP response with the Excel file
        response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'
        return response

    generate_excel_report.short_description = "Generate Excel Report"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('generate_excel_report/', self.admin_site.admin_view(self.generate_excel_report), name='generate_excel_report'),
        ]
        return custom_urls + urls


admin.site.register(SalesData, SalesDataAdmin)
