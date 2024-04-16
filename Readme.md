#Virtual Environment Activation in my PC
    -source /Users/aniketrajsingh/Documents/GitHub/ecommerce_website/venv/bin/activate

#Virtual Environment Activation in your PC
    -source /location.../ecommerce_website/venv/bin/activate

#Backup Database

    -python manage.py dumpdata > backup.json
            OR
    -pip install PyYAML
    -python manage.py dumpdata --format=yaml > backup.yaml

#Restore Data

    -python manage.py loaddata backup.json
    -python manage.py loaddata backup.yaml

#Create the cron table in your Django project:

    -python manage.py crontab add

#If you want to check the cron jobs, you can run:

    -python manage.py crontab show

#If you need to delete the cron table:

    -python manage.py crontab remove