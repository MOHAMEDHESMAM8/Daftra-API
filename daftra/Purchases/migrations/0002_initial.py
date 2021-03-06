# Generated by Django 3.2.8 on 2021-12-18 16:18

import Users.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Users', '0001_initial'),
        ('Purchases', '0001_initial'),
        ('Store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchasepayments',
            name='Collected_by',
            field=models.ForeignKey(db_column='Collected_by', on_delete=models.SET(Users.models.get_deleted_employee), to='Users.employees'),
        ),
        migrations.AddField(
            model_name='purchasepayments',
            name='purchase_invoice',
            field=models.ForeignKey(db_column='purchase_invoice', on_delete=django.db.models.deletion.CASCADE, related_name='PurchasePayments', to='Purchases.purchaseinvoice'),
        ),
        migrations.AddField(
            model_name='purchaseinvoice_products',
            name='product',
            field=models.ForeignKey(db_column='product', on_delete=django.db.models.deletion.PROTECT, to='Store.products'),
        ),
        migrations.AddField(
            model_name='purchaseinvoice_products',
            name='purchase_invoice',
            field=models.ForeignKey(db_column='purchase_invoice', on_delete=django.db.models.deletion.CASCADE, related_name='PurchaseInvoice_products', to='Purchases.purchaseinvoice'),
        ),
        migrations.AddField(
            model_name='purchaseinvoice_products',
            name='tax1',
            field=models.ForeignKey(blank=True, db_column='tax1', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='PurchaseInvoice_tax', to='Users.tax'),
        ),
        migrations.AddField(
            model_name='purchaseinvoice_products',
            name='tax2',
            field=models.ForeignKey(blank=True, db_column='tax2', null=True, on_delete=django.db.models.deletion.PROTECT, to='Users.tax'),
        ),
        migrations.AddField(
            model_name='purchaseinvoice',
            name='add_by',
            field=models.ForeignKey(db_column='add_by', on_delete=models.SET(Users.models.get_deleted_employee), to='Users.employees'),
        ),
        migrations.AddField(
            model_name='purchaseinvoice',
            name='supplier',
            field=models.ForeignKey(db_column='supplier', on_delete=django.db.models.deletion.CASCADE, to='Users.suppliers'),
        ),
        migrations.AddField(
            model_name='purchaseinvoice',
            name='warehouse',
            field=models.ForeignKey(db_column='warehouse', on_delete=django.db.models.deletion.PROTECT, to='Store.warehouses'),
        ),
    ]
