# Generated by Django 3.2.8 on 2021-12-18 16:18

import Users.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Users', '0001_initial'),
        ('Store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='supplier',
            field=models.ForeignKey(db_column='supplier', on_delete=django.db.models.deletion.CASCADE, related_name='supplier', to='Users.suppliers'),
        ),
        migrations.AddField(
            model_name='product_count',
            name='product',
            field=models.ForeignKey(db_column='product', on_delete=django.db.models.deletion.CASCADE, related_name='Product_count', to='Store.products'),
        ),
        migrations.AddField(
            model_name='product_count',
            name='warehouse',
            field=models.ForeignKey(db_column='warehouse', on_delete=django.db.models.deletion.CASCADE, to='Store.warehouses'),
        ),
        migrations.AddField(
            model_name='outpermissions_products',
            name='out_permission',
            field=models.ForeignKey(db_column='out_permission', on_delete=django.db.models.deletion.CASCADE, related_name='OutPermissions_Products', to='Store.outpermissions'),
        ),
        migrations.AddField(
            model_name='outpermissions_products',
            name='product',
            field=models.ForeignKey(db_column='product', on_delete=django.db.models.deletion.PROTECT, related_name='OutPermissions_Products', to='Store.products'),
        ),
        migrations.AddField(
            model_name='outpermissions',
            name='add_by',
            field=models.ForeignKey(db_column='add_by', on_delete=models.SET(Users.models.get_deleted_employee), to='Users.employees'),
        ),
        migrations.AddField(
            model_name='outpermissions',
            name='warehouse',
            field=models.ForeignKey(db_column='warehouse', on_delete=django.db.models.deletion.CASCADE, to='Store.warehouses'),
        ),
        migrations.AddField(
            model_name='addpermissions_products',
            name='add_permission',
            field=models.ForeignKey(db_column='add_permission', on_delete=django.db.models.deletion.CASCADE, related_name='AddPermissions_Products', to='Store.addpermissions'),
        ),
        migrations.AddField(
            model_name='addpermissions_products',
            name='product',
            field=models.ForeignKey(db_column='product', on_delete=django.db.models.deletion.PROTECT, related_name='AddPermissions_Products', to='Store.products'),
        ),
        migrations.AddField(
            model_name='addpermissions',
            name='add_by',
            field=models.ForeignKey(db_column='add_by', on_delete=models.SET(Users.models.get_deleted_employee), to='Users.employees'),
        ),
        migrations.AddField(
            model_name='addpermissions',
            name='warehouse',
            field=models.ForeignKey(db_column='warehouse', on_delete=django.db.models.deletion.CASCADE, to='Store.warehouses'),
        ),
    ]
