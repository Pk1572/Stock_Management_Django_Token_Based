# Generated by Django 5.1.4 on 2024-12-16 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=255)),
                ('company_address', models.TextField()),
                ('phone_number', models.CharField(max_length=15)),
            ],
        ),
    ]
