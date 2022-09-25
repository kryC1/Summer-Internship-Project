from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('waiting_tickets/', views.getWaitingTickets, name ='getWaitingTickets'),
    path('done_tickets/', views.getDoneTickets, name ='getDoneTickets'),
    path('pend/', views.pend, name = 'pend'),
    path('create/', views.createTicket, name = 'create'),
    path('getTicket/<str:pk>', views.getTicket, name = 'getTicket'),
    path('globalID/', views.updateGlobalID, name = 'updateGlobal'),
    path('monthChart/', views.monthChart, name = 'monthChart'),
    path('adminDashboard/' , views.adminDashboard, name = "adminDashboard"),
    path("refresh_waiting_table/", views.refreshWaitingTable, name ='refreshWaitTable'),
    path("refresh_done_table/", views.refreshDoneTable, name ='refreshDoneTable'),
    path("userChart/", views.userChart, name = "userChart"),
    path("setDates/", views.setDates, name = "setDates"),
    path("setID/", views.setUserID, name = "setID"),
    #path('updateTickets/', views.updateTickets, name = 'updateTickets'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
