from django.conf import settings
from django.core.management import call_command
from django_cron import CronJobBase, Schedule
from .models import BackupLog
import os

class BackupTask(CronJobBase):
    RUN_AT_TIMES = ['00:00']  # Run every day at 12 am

    schedule = Schedule(run_at_times=RUN_AT_TIMES)

    def do(self):
        self.stdout.write("Starting database backup...")
        self.stdout.flush()
        # Execute the backup command
        call_command('dbbackup')
        self.stdout.write("Database backup completed successfully.")
        self.stdout.flush()
        backup_log = BackupLog.objects.create()
        backup_log.save()

class BackupRemovalTask(CronJobBase):
    RUN_EVERY_MINS = 24 * 60 * 10  # Run every 10 days
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

    def do(self):
        self.stdout.write("Removing previous backups except for the last one...")
        self.stdout.flush()
        
        backup_dir = settings.DBBACKUP_STORAGE_OPTIONS.get('location')
        backups = sorted(os.listdir(backup_dir), key=os.path.getmtime)
        backups_to_remove = backups[:-1]
        
        if len(backups_to_remove) > 0:
            for backup_file in backups_to_remove:
                os.remove(os.path.join(backup_dir, backup_file))
                self.stdout.write(f"Removed previous backup: {backup_file}")
                self.stdout.flush()