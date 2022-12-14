# Generated by Django 3.2.10 on 2022-07-28 09:39

import apps.home.models
from django.db import migrations, models
import django_enumfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=255)),
                ('lastname', models.CharField(max_length=255)),
                ('subject', models.CharField(max_length=255)),
                ('scenario', models.CharField(max_length=2000)),
                ('date', models.DateTimeField()),
                ('email', models.EmailField(max_length=254, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TicketDataTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=255)),
                ('lastname', models.CharField(max_length=255)),
                ('subject', models.CharField(max_length=255)),
                ('scenario', models.CharField(max_length=2000)),
                ('date', models.DateTimeField()),
                ('operation_flag', django_enumfield.db.fields.EnumField(enum=apps.home.models.Operations)),
                ('status_flag', django_enumfield.db.fields.EnumField(enum=apps.home.models.Status)),
                ('email', models.EmailField(max_length=254, null=True)),
            ],
        ),
    ]
