#Virtual Environment Activation in my PC
source /Users/aniketrajsingh/Documents/GitHub/ecommerce_website/venv/bin/activate

#Virtual Environment Activation in your PC
source /location.../ecommerce_website/venv/bin/activate

#Backup Database

-python manage.py dumpdata > backup.json

-pip install PyYAML
-python manage.py dumpdata --format=yaml > backup.yaml

#Restore Data

-python manage.py loaddata backup.json
-python manage.py loaddata backup.yaml

