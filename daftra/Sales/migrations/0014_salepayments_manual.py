# Generated by Django 3.2.8 on 2021-11-18 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Sales', '0013_alter_salepayments_collected_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='salepayments',
            name='manual',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
    ]
