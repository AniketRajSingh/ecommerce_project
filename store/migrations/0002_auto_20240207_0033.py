# Generated by Django 3.2 on 2024-02-07 00:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='permanent_city',
            new_name='city',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='permanent_landmark',
            new_name='landmark',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='permanent_pincode',
            new_name='pincode',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='permanent_state',
            new_name='state',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='permanent_street',
            new_name='street',
        ),
    ]
