# Generated by Django 5.1.4 on 2024-12-17 12:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('productapi', '0008_alter_history_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productstock',
            old_name='product_id',
            new_name='product',
        ),
    ]
