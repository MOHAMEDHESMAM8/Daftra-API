# Generated by Django 3.2.8 on 2021-10-25 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0008_tax'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suppliers',
            name='Tax_id',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='suppliers',
            name='commercial_record',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]