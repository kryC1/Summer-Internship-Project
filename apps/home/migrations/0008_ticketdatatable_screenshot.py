# Generated by Django 3.2.10 on 2022-08-01 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_remove_ticketdatatable_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketdatatable',
            name='screenshot',
            field=models.ImageField(null=True, upload_to=None),
        ),
    ]
