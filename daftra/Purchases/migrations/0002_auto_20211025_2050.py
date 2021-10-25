# Generated by Django 3.2.8 on 2021-10-25 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Purchases', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchasepayments',
            old_name='attachments',
            new_name='attachment',
        ),
        migrations.AddField(
            model_name='purchaseinvoice',
            name='total',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='purchaseinvoice_products',
            name='count_after',
            field=models.SmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]
