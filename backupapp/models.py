from django.db import models

class BackupLog(models.Model):
    backup_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Backup on {self.backup_date}"