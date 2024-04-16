from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderViewSet, SalesDataViewSet, restore_backup, BackupLogListAPIView, create_backup

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'salesdata', SalesDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('backup-logs/', BackupLogListAPIView.as_view(), name='backup_log_list_api'),
    path('restore-backup/', restore_backup, name='restore_backup'),
    path('create_backup/', create_backup, name='create_backup'),

]