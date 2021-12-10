# Generated by Django 3.2.8 on 2021-11-22 06:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0012_auto_20211120_1008'),
        ('Sales', '0015_alter_salepayments_manual'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saleinvoice',
            name='customer',
            field=models.ForeignKey(db_column='customer', on_delete=django.db.models.deletion.CASCADE, related_name='SaleInvoice_customer', to='Users.customers'),
        ),
        migrations.AlterField(
            model_name='saleinvoice',
            name='sold_by',
            field=models.ForeignKey(db_column='sold_by', on_delete=django.db.models.deletion.CASCADE, related_name='SaleInvoice_employee', to='Users.employees'),
        ),
    ]