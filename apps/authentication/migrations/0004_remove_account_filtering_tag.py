# Generated by Django 3.2.6 on 2022-08-04 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_account_filtering_tag'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='filtering_tag',
        ),
    ]
