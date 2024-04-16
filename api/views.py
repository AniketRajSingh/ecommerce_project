from rest_framework import viewsets
from store.models import Product, Order, SalesData
from backupapp.models import BackupLog
from rest_framework import serializers
from rest_framework import generics
from django.core.management import call_command
from django.http import JsonResponse
from backupapp.models import BackupLog
from django.conf import settings
import os
import subprocess

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class SalesDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesData
        fields = '__all__'

class SalesDataViewSet(viewsets.ModelViewSet):
    queryset = SalesData.objects.all()
    serializer_class = SalesDataSerializer

class BackupLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupLog
        fields = '__all__'

class BackupLogListAPIView(generics.ListAPIView):
    queryset = BackupLog.objects.all()
    serializer_class = BackupLogSerializer

def restore_backup(request):
    # Get the backup directory from settings
    backup_directory = settings.DBBACKUP_STORAGE_OPTIONS.get('location')
    
    # Check if the backup directory exists
    if not os.path.isdir(backup_directory):
        print(f"Backup directory '{backup_directory}' does not exist.")
        return JsonResponse({'error': f"Backup directory '{backup_directory}' does not exist."}, status=500)
    
    # List all backup files in the directory
    backup_files = [f for f in os.listdir(backup_directory) if f.endswith('.dump')]
    
    # Check if there are any backup files
    if not backup_files:
        print("No backup files found in the directory.")
        return JsonResponse({'error': "No backup files found in the directory."}, status=500)
    
    # Find the latest backup file based on modification time
    latest_backup_file = max(backup_files, key=lambda f: os.path.getmtime(os.path.join(backup_directory, f)))
    print(latest_backup_file)
    latest_backup_file_path = os.path.join(backup_directory, latest_backup_file)
    print(latest_backup_file_path)
    
    try:
        # Execute the dbrestore command with the latest backup file path
        proc = subprocess.Popen(['python', 'manage.py', 'dbrestore','-i', latest_backup_file], stdin=subprocess.PIPE)
        proc.communicate(input=b'Y\n')  # Send 'Y' as input
        return JsonResponse({'message': 'Database restored successfully'})
    except subprocess.CalledProcessError as e:
        # Handle any errors that might occur during the restore process
        error_message = str(e)
        print(f"Error occurred during database restore: {error_message}")
        return JsonResponse({'error': error_message}, status=500)

def create_backup(request):
    try:
        # Assuming 'dbbackup' is the management command to perform the database backup
        call_command('dbbackup')
        backup_log = BackupLog.objects.create()
        backup_log.save()
        return JsonResponse({'message': 'Database backup was successful'}, status=200)
    except Exception as e:
        # Handle any errors that might occur during the backup process
        return JsonResponse({'error': str(e)}, status=500)