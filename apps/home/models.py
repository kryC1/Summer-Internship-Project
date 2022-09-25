from django.db import models
from django.contrib.auth.models import User
from django_enumfield import enum


class Ticket(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    scenario = models.CharField(max_length=2000)
    date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(null=True)


class Operations(enum.Enum):
    Unprocessed = 0
    Cleaned = 1
    Rejected = 2


class Status(enum.Enum):
    inProgress = 2
    Closed = 1
    Waiting = 0


class TicketDataTable(models.Model):
    fullname = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    scenario = models.CharField(max_length=2000)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    operation_flag = enum.EnumField(Operations)
    status_flag = enum.EnumField(Status)
    email = models.EmailField(null=True)
    domain = models.CharField(null = True, max_length = 255, default="none")
    imageName = models.CharField(max_length = 255, null = True)


class TicketOperationTable(models.Model):
    user_id = models.IntegerField()
    ticket_id = models.IntegerField()
    operation_flag = enum.EnumField(Operations)
    date = models.DateField(auto_now_add = True)


# Create your models here.

