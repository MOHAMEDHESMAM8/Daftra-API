# Generated by Django 3.2.8 on 2021-12-13 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Purchases', '0007_purchasepayments_purchase_invoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseinvoice',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]