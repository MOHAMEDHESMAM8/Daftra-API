# Generated by Django 3.2.8 on 2021-11-09 22:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Sales', '0005_auto_20211102_1043'),
    ]

    operations = [
        migrations.RenameField(
            model_name='saleinvoice_products',
            old_name='purchase_invoice',
            new_name='sales_invoice',
        ),
    ]