# Generated by Django 3.2.8 on 2021-12-04 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0017_suppliers_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='suppliers',
            name='currency',
        ),
    ]
