from django.contrib import admin
from .models import TicketDataTable, Ticket

admin.site.register(Ticket)
admin.site.register(TicketDataTable)
