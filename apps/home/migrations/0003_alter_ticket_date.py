# Generated by Django 4.0.6 on 2022-07-28 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_ticketdatatable_domain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
