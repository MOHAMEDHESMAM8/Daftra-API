# Generated by Django 3.2.8 on 2021-11-18 11:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0011_auto_20211102_1043'),
        ('Sales', '0012_alter_salepayments_collected_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salepayments',
            name='Collected_by',
            field=models.ForeignKey(db_column='Collected_by', on_delete=django.db.models.deletion.CASCADE, related_name='SalePayments_user', to='Users.employees'),
        ),
    ]