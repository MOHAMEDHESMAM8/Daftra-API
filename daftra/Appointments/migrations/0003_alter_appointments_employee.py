# Generated by Django 3.2.8 on 2021-12-10 12:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0019_auto_20211210_1447'),
        ('Appointments', '0002_auto_20211102_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointments',
            name='employee',
            field=models.ForeignKey(blank=True, db_column='employee', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment_employee', to='Users.employees'),
        ),
    ]