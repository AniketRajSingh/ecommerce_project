from django.contrib import admin
from .models import Category, Quantity, Product, Order, OrderItem, ProductQuantity, Media, Cancellation, SalesData
from django.db.models.functions import TruncDate
from django.db.models import Sum, Count
import pandas as pd
from io import BytesIO
from django.http import HttpResponse

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
        # Logic to get data for Sales Chart with date filter
        start_date = request.GET.get('date__gte')
        end_date = request.GET.get('date__lte')

        # Logic to get data for Sales Chart based on the selected date range
        queryset = SalesData.objects.all()

        # Apply date range filter only if both start_date and end_date are provided
        if start_date and end_date:
            queryset = queryset.filter(date__range=(start_date, end_date))

        aggregated_data = queryset.annotate(chart_date=TruncDate('date')).values('chart_date').annotate(revenue=Sum('total_sales')).order_by('chart_date')
        chart_data = list(aggregated_data)
        for entry in chart_data:
            entry['chart_date'] = entry['chart_date'].isoformat()
            entry['revenue'] = float(entry['revenue'])

        # Logic to get data for Product Quantity chart with date filter
        if start_date and end_date:
            product_quantity_data = OrderItem.objects.filter(order__created_at__date__gte=start_date, order__created_at__date__lte=end_date) \
                .values('product__name') \
                .annotate(total_quantity=Sum('item_quantity'))
            product_quantity_chart_data = list(product_quantity_data)
        else:
            product_quantity_chart_data = list(OrderItem.objects.values('product__name').annotate(total_quantity=Sum('item_quantity')))
        for entry in product_quantity_chart_data:
                entry['product_name'] = entry['product__name']
                entry['total_quantity'] = float(entry['total_quantity'])

        # Logic to get data for Order Status chart with date filter
        if start_date and end_date:
            order_status_data = Order.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date) \
                .values('delivery_status') \
                .annotate(total_orders=Count('id'))
            order_status_chart_data = list(order_status_data)
        else:
            order_status_chart_data = list(Order.objects.values('delivery_status').annotate(total_orders=Count('id')))
        for entry in order_status_chart_data:
                entry['delivery_status'] = entry['delivery_status']
                entry['total_orders'] = float(entry['total_orders'])

        extra_context = extra_context or {}
        extra_context['chart_data'] = chart_data
        extra_context['product_quantity_data'] = product_quantity_chart_data
        extra_context['order_status_data'] = order_status_chart_data
        return super().changelist_view(request, extra_context=extra_context)

    def generate_excel_report(self, request, queryset):
        # Create an Excel writer with the xlsxwriter engine
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')

        # Get the number format for the 'Revenue' column
        num_format = writer.book.add_format({'num_format': '#,##0.00'})
        # Get the center align format
        center_align = writer.book.add_format({'align': 'center', 'valign': 'vcenter'})

        # Get data for Sales Chart
        chart_data = queryset.annotate(chart_date=TruncDate('date')).values('chart_date').annotate(revenue=Sum('total_sales')).order_by('chart_date')
        chart_data = list(chart_data)

        # Extract dates from SalesData queryset
        sales_data_dates = [sales_data.date for sales_data in queryset]

        # Get data for Product Quantity chart based on SalesData dates
        product_quantity_data_by_date = OrderItem.objects.filter(order__created_at__date__in=sales_data_dates) \
            .values('product__name') \
            .annotate(total_quantity=Sum('item_quantity'))
        product_quantity_chart_data_by_date = list(product_quantity_data_by_date)

        # Get data for Order Status chart based on SalesData dates
        order_status_data_by_date = Order.objects.filter(created_at__date__in=sales_data_dates) \
            .values('delivery_status') \
            .annotate(total_orders=Count('id'))
        order_status_chart_data_by_date = list(order_status_data_by_date)

        # Get data for Order table based on SalesData dates
        order_data_by_date = Order.objects.filter(created_at__date__in=sales_data_dates) \
            .values('id', 'delivery_status', 'user__username', 'total_price', 'created_at')
        df_order_by_date = pd.DataFrame(list(order_data_by_date))

        # Convert timestamps to the appropriate format
        df_order_by_date['created_at'] = df_order_by_date['created_at'].dt.strftime('%b. %d, %Y, %I:%M %p')

        # Write each DataFrame to a different sheet for data based on SalesData dates
        df_sales = pd.DataFrame(chart_data)
        df_sales.to_excel(writer, sheet_name='SalesData', index=False)

        df_product_quantity_by_date = pd.DataFrame(product_quantity_chart_data_by_date)
        df_product_quantity_by_date.to_excel(writer, sheet_name='ProductQuantity', index=False)

        df_order_status_by_date = pd.DataFrame(order_status_chart_data_by_date)
        df_order_status_by_date.to_excel(writer, sheet_name='OrderStatus', index=False)

        df_order_by_date.to_excel(writer, sheet_name='OrderData', index=False)

        # Access the xlsxwriter workbook and worksheet objects directly
        workbook = writer.book
        worksheet_sales = writer.sheets['SalesData']
        worksheet_product_quantity = writer.sheets['ProductQuantity']
        worksheet_order_status = writer.sheets['OrderStatus']
        worksheet_order_data = writer.sheets['OrderData']
        worksheet_sales.write_column('B2', df_sales['revenue'], num_format)
        worksheet_product_quantity.write_column('B2', df_product_quantity_by_date['total_quantity'], num_format)

        # Create a chart object for the Sales Chart
        sales_chart = workbook.add_chart({'type': 'line'})
        sales_chart.add_series({'values': '=SalesData!$B$2:$B${}'.format(len(chart_data) + 1),
                                'name': 'Revenue'})
        sales_chart.set_title({'name': 'Sales Chart'})
        sales_chart.set_x_axis({'name': 'Date'})
        sales_chart.set_y_axis({'name': 'Revenue'})
        worksheet_sales.insert_chart('D2', sales_chart)

        # Create a column chart for the Product Quantity
        product_quantity_chart = workbook.add_chart({'type': 'column'})
        product_quantity_chart.add_series({'values': '=ProductQuantity!$B$2:$B${}'.format(len(df_product_quantity_by_date) + 1),
                                           'name': 'Total Quantity'})
        product_quantity_chart.set_title({'name': 'Product Quantity Chart'})
        product_quantity_chart.set_x_axis({'name': 'Product'})
        product_quantity_chart.set_y_axis({'name': 'Total Quantity'})
        worksheet_product_quantity.insert_chart('D2', product_quantity_chart)

        # Create a pie chart for the Order Status
        order_status_chart = workbook.add_chart({'type': 'pie'})
        order_status_chart.add_series({'values': '=OrderStatus!$B$2:$B${}'.format(len(df_order_status_by_date) + 1),
                                       'name': 'Total Orders'})
        order_status_chart.set_title({'name': 'Order Status Chart'})
        worksheet_order_status.insert_chart('D2', order_status_chart)


        # Add Order data to the 'OrderData' sheet
        worksheet_order_data.merge_range('A1:E1', 'Order Data', center_align)
        worksheet_order_data.write('A1', 'Order Data:')
        worksheet_order_data.write('A2', 'ID')
        worksheet_order_data.write('B2', 'Delivery Status')
        worksheet_order_data.write('C2', 'User')
        worksheet_order_data.write('D2', 'Total Price')
        worksheet_order_data.write('E2', 'Created At')

        # Center align all cells in all sheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for col_num, value in enumerate(df_order_by_date.columns.values):
                worksheet.set_column(col_num, col_num, None, center_align)

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
