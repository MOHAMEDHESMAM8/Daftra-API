# Generated by Django 3.2.8 on 2021-11-13 22:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Sales', '0007_alter_saleinvoice_products_sales_invoice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='saleinvoice_products',
            name='sales_invoice',
            field=models.ForeignKey(db_column='sales_invoice', on_delete=django.db.models.deletion.CASCADE, related_name='SaleInvoice_products', to='Sales.saleinvoice'),
        ),
    ]
