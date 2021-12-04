# Generated by Django 3.2.8 on 2021-12-04 06:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0016_alter_recordhistory_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='suppliers',
            name='user',
            field=models.OneToOneField(db_column='user', default=1, on_delete=django.db.models.deletion.CASCADE, related_name='supplier', to='Users.user'),
            preserve_default=False,
        ),
    ]
