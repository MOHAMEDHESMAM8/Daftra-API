# Generated by Django 3.2.8 on 2021-12-18 16:18

import Users.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Users', '0001_initial'),
        ('Sales', '0001_initial'),
        ('Store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='salepayments',
            name='Collected_by',
            field=models.ForeignKey(db_column='Collected_by', on_delete=models.SET(Users.models.get_deleted_employee), related_name='SalePayments_user', to='Users.employees'),
        ),
        migrations.AddField(
            model_name='salepayments',
            name='sales_invoice',
            field=models.ForeignKey(db_column='sales_invoice', on_delete=django.db.models.deletion.CASCADE, related_name='SalePayments', to='Sales.saleinvoice'),
        ),
        migrations.AddField(
            model_name='saleinvoice_products',
            name='product',
            field=models.ForeignKey(db_column='product', on_delete=django.db.models.deletion.PROTECT, related_name='SaleInvoice', to='Store.products'),
        ),
        migrations.AddField(
            model_name='saleinvoice_products',
            name='sales_invoice',
            field=models.ForeignKey(db_column='sales_invoice', on_delete=django.db.models.deletion.CASCADE, related_name='SaleInvoice_products', to='Sales.saleinvoice'),
        ),
        migrations.AddField(
            model_name='saleinvoice_products',
            name='tax1',
            field=models.ForeignKey(blank=True, db_column='tax1', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='saleseInvoice_tax', to='Users.tax'),
        ),
        migrations.AddField(
            model_name='saleinvoice_products',
            name='tax2',
            field=models.ForeignKey(blank=True, db_column='tax2', null=True, on_delete=django.db.models.deletion.PROTECT, to='Users.tax'),
        ),
        migrations.AddField(
            model_name='saleinvoice',
            name='customer',
            field=models.ForeignKey(db_column='customer', on_delete=django.db.models.deletion.CASCADE, related_name='SaleInvoice_customer', to='Users.customers'),
        ),
        migrations.AddField(
            model_name='saleinvoice',
            name='sales_officer',
            field=models.ForeignKey(blank=True, db_column='sales_officer', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales_officer', to='Users.employees'),
        ),
        migrations.AddField(
            model_name='saleinvoice',
            name='sold_by',
            field=models.ForeignKey(db_column='sold_by', on_delete=models.SET(Users.models.get_deleted_employee), related_name='SaleInvoice_employee', to='Users.employees'),
        ),
        migrations.AddField(
            model_name='saleinvoice',
            name='warehouse',
            field=models.ForeignKey(db_column='warehouse', on_delete=django.db.models.deletion.PROTECT, to='Store.warehouses'),
        ),
    ]
