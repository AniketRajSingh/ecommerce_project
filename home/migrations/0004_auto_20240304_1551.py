# Generated by Django 3.2 on 2024-03-04 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_homepage_homepagepopup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepagecarousel',
            name='media_url',
            field=models.FileField(upload_to='homepagecarousel/'),
        ),
        migrations.AlterField(
            model_name='homepagepopup',
            name='image_url',
            field=models.FileField(upload_to='popup_images/'),
        ),
        migrations.AlterField(
            model_name='review',
            name='photo_url',
            field=models.FileField(blank=True, null=True, upload_to='review_images/'),
        ),
    ]
