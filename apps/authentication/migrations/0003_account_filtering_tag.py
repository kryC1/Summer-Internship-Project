# Generated by Django 3.2.6 on 2022-08-04 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_alter_account_per_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='filtering_tag',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
