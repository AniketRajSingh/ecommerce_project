# Generated by Django 3.2 on 2024-02-07 03:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HomePageCarousel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_type', models.CharField(choices=[('image', 'Image'), ('video', 'Video')], default='image', max_length=10)),
                ('media_url', models.URLField()),
                ('image_description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='HomePagePopup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('image_url', models.URLField()),
                ('description', models.TextField()),
                ('button_name', models.CharField(max_length=255)),
                ('redirection_link', models.URLField()),
                ('display_on_homepage', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('review_text', models.TextField()),
                ('photo_url', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HomePage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected_popup', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.homepagepopup')),
            ],
        ),
    ]
