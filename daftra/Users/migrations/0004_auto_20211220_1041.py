# Generated by Django 3.2.8 on 2021-12-20 08:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0003_auto_20211219_2330'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotesActions',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('customer', 'customer'), ('employee', 'employee')], max_length=20)),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='notes',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notes',
            name='action',
            field=models.ForeignKey(blank=True, db_column='action', null=True, on_delete=django.db.models.deletion.SET_NULL, to='Users.notesactions'),
        ),
    ]
