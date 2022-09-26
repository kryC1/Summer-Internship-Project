# Generated by Django 3.2.10 on 2022-08-02 13:23

import apps.home.models
from django.db import migrations, models
import django_enumfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_auto_20220801_1653'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketOperationTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('ticket_id', models.IntegerField()),
                ('operation_flag', django_enumfield.db.fields.EnumField(enum=apps.home.models.Operations)),
                ('date', models.DateField(auto_now_add=True)),
            ],
        ),
    ]
