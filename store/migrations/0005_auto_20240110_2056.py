# Generated by Django 3.2 on 2024-01-10 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_order_final_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='final_price',
        ),
        migrations.AddField(
            model_name='product',
            name='final_price',
            field=models.DecimalField(decimal_places=2, default=100, max_digits=10),
            preserve_default=False,
        ),
    ]