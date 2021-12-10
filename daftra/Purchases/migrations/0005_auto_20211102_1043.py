# Generated by Django 3.2.8 on 2021-11-02 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Purchases', '0004_rename_attachments_attachments_attachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseinvoice',
            name='Update_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='attachments',
            name='attachment',
            field=models.FileField(upload_to='Files/%y/%m'),
        ),
        migrations.AlterField(
            model_name='purchasepayments',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='Files/%y/%m'),
        ),
    ]