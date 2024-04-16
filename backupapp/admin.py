from django.contrib import admin
from django_cron.models import CronJobLog, CronJobLock

# Unregister the CronJobLog model
admin.site.unregister(CronJobLog)
admin.site.unregister(CronJobLock)
