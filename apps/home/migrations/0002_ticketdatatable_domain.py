# Generated by Django 3.2.10 on 2022-07-28 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketdatatable',
            name='domain',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
