# Generated by Django 3.2 on 2024-02-20 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_productquantity_bestsellers_img_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productquantity',
            name='bestsellers_img_url',
        ),
        migrations.AddField(
            model_name='product',
            name='bestsellers_img_url',
            field=models.URLField(default=1),
            preserve_default=False,
        ),
    ]
