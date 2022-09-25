#region imports
from django import template
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Ticket, TicketDataTable, Operations, Status, TicketOperationTable
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.paginator import Paginator
from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict
from time import sleep
import re, string, random, os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from PIL import Image
from datetime import date, timedelta
import datetime
from django.db.models import Q
from django.contrib.auth.models import User
import calendar
#endregion


# ------------------------------------------------
#global variables
globalID = 1  # To keep track of which ticket we are processing
globalPage = 1
dateOption = 0
# ------------------------------------------------

# Filtering inputs--------------------------------
filter_name = ""
filter_email = ""
filter_domain = ""
filter_subject = ""
filter_process = ""
# ------------------------------------------------


#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
#region bootstrap
@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/home.html')
    return HttpResponse(html_template.render(context, request))


def home(request):
    return render(request, 'home/home.html', {})


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
#endregion
#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*



#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
#region tables and updating tables


# Whenever the inspect button is pressed, this function makes sure that the operations are performed on that ticket
@csrf_exempt
def updateGlobalID(request):
    global globalID

    if request.is_ajax():
        globalID = request.POST.get("tid")

    return Response()

# Renders the dashboard that shows tickets for 'WAITING'
@login_required()
def getWaitingTickets(request):
    global globalPage
    global globalID

    myuser = request.user

    # Filtering inputs----------------------------
    global filter_name
    global filter_email
    global filter_domain
    global filter_subject

    if request.GET.get("filter_name") != None:
        filter_name = request.GET.get("filter_name")

    if request.GET.get("filter_email") != None:
        filter_email = request.GET.get("filter_email")

    if request.GET.get("filter_domain") != None:
        filter_domain = request.GET.get("filter_domain")

    if request.GET.get("filter_subject") != None:
        if request.GET.get("filter_subject") == "all":
            filter_subject = ""
        else:
            filter_subject = request.GET.get("filter_subject")
    # --------------------------------------------

    # Paginator-----------------------------------
    page_num = int(request.GET.get('pg_num') or myuser.account.per_page)
    myuser.account.per_page = page_num
    myuser.account.save()
    # --------------------------------------------

    # User verification--> Users can only see subject that they are assigned to
    if request.user.groups.filter(name="bug_report"):
        ticket_list1 = TicketDataTable.objects.filter(operation_flag=0, subject="Bug Report")
    else:
        ticket_list1 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="false_positive"):
        ticket_list2 = TicketDataTable.objects.filter(operation_flag=0, subject="False Positive")
    else:
        ticket_list2 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="suggestions"):
        ticket_list3 = TicketDataTable.objects.filter(operation_flag=0, subject="Suggestion & Ideas")
    else:
        ticket_list3 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="academic"):
        ticket_list4 = TicketDataTable.objects.filter(operation_flag=0, subject="Academic Request")
    else:
        ticket_list4 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="other"):
        ticket_list5 = TicketDataTable.objects.filter(operation_flag=0, subject="Other Topics")
    else:
        ticket_list5 = TicketDataTable.objects.none()

    temp_list = ticket_list1 | ticket_list2 | ticket_list3 | ticket_list4 | ticket_list5

    new_list = temp_list.filter(domain__contains=filter_domain,
                                    fullname__icontains=filter_name,
                                    email__startswith=filter_email,
                                    subject__startswith=filter_subject)
    p = Paginator(new_list.order_by("-date_created").values(), myuser.account.per_page)
    globalPage = request.GET.get('page')
    ticket_list = p.get_page(globalPage)
    # --------------------------------------------


    # Submitting operation------------------------
    ticket = TicketDataTable.objects.all()
    if request.method == 'POST':
        ticket = TicketDataTable.objects.get(id=globalID)
        val = request.POST.get('op_select')

        if (val == "1"):  # Accepted
            ticket.operation_flag = int(val)
            ticket.status_flag = 1
            ticket.save()
            ticketRow = TicketOperationTable(user_id = request.user.id, ticket_id = ticket.id, operation_flag = 1)
            ticketRow.save()
            return redirect('http://127.0.0.1:8000/waiting_tickets/')
        elif (val == "2"):  # Rejected
            ticket.operation_flag = int(val)
            ticket.status_flag = 1
            ticket.save()
            ticketRow = TicketOperationTable(user_id = request.user.id, ticket_id = ticket.id, operation_flag = 2)
            ticketRow.save()
            return redirect('http://127.0.0.1:8000/waiting_tickets/')
        elif (val == "0"):  # Don't Change
            ticket.operation_flag = int(val)
            ticket.status_flag = 0
            ticket.save()
            ticketRow = TicketOperationTable(user_id = request.user.id, ticket_id = ticket.id, operation_flag = 0)
            ticketRow.save()
            return redirect('http://127.0.0.1:8000/waiting_tickets/')
        else:
            ticket.operation_flag = int(val)
            ticket.status_flag = 0
            ticket.save()
            return redirect('http://127.0.0.1:8000/waiting_tickets/')
    # --------------------------------------------

    context = {
        'ticket_list': ticket_list,
    }

    return render(request, "home/ui-tables-wait.html", context)


# Renders the dashboard that shows tickets for 'DONE'
@login_required()
def getDoneTickets(request):
    global globalPage
    global globalID

    myuser = request.user

    # Filtering inputs----------------------------
    global filter_name
    global filter_email
    global filter_domain
    global filter_subject
    global filter_process

    if request.GET.get("filter_name") != None:
        filter_name = request.GET.get("filter_name")

    if request.GET.get("filter_email") != None:
        filter_email = request.GET.get("filter_email")

    if request.GET.get("filter_domain") != None:
        filter_domain = request.GET.get("filter_domain")

    if request.GET.get("filter_subject") != None:
        if request.GET.get("filter_subject") == "all":
            filter_subject = ""
        else:
            filter_subject = request.GET.get("filter_subject")

    if request.GET.get("filter_process") != None:
        if request.GET.get("filter_process") == "all":
            filter_process = ""
        else:
            filter_process = request.GET.get("filter_process")

    # --------------------------------------------

    # Paginator-----------------------------------
    page_num = int(request.GET.get('pg_num') or myuser.account.per_page)
    myuser.account.per_page = page_num
    myuser.account.save()
    # --------------------------------------------

    # User verification--> Users can only see subject that they are assigned to
    if request.user.groups.filter(name="bug_report"):
        ticket_list1 = TicketDataTable.objects.filter(Q(operation_flag=1) | Q(operation_flag=2), subject="Bug Report")
    else:
        ticket_list1 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="false_positive"):
        ticket_list2 = TicketDataTable.objects.filter(Q(operation_flag=1) | Q(operation_flag=2), subject="False Positive")
    else:
        ticket_list2 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="suggestions"):
        ticket_list3 = TicketDataTable.objects.filter(Q(operation_flag=1) | Q(operation_flag=2), subject="Suggestion & Ideas")
    else:
        ticket_list3 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="academic"):
        ticket_list4 = TicketDataTable.objects.filter(Q(operation_flag=1) | Q(operation_flag=2), subject="Academic Request")
    else:
        ticket_list4 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="other"):
        ticket_list5 = TicketDataTable.objects.filter(Q(operation_flag=1) | Q(operation_flag=2), subject="Other Topics")
    else:
        ticket_list5 = TicketDataTable.objects.none()

    temp_list = ticket_list1 | ticket_list2 | ticket_list3 | ticket_list4 | ticket_list5
    new_list = temp_list.filter(fullname__icontains=filter_name,
                                email__startswith=filter_email,
                                domain__contains=filter_domain,
                                subject__startswith=filter_subject,
                                operation_flag__startswith=filter_process)
    p = Paginator(new_list.order_by("-date_updated").values(), myuser.account.per_page)
    globalPage = request.GET.get('page')
    ticket_list = p.get_page(globalPage)
    # --------------------------------------------

    # Submitting operation------------------------
    ticket = TicketDataTable.objects.all()
    if request.method == 'POST':
        ticket = TicketDataTable.objects.get(id=globalID)
        val = request.POST.get('op_select')

        if (val == "1"):  # Accepted
            ticket.operation_flag = int(val)
            ticket.status_flag = 1
            ticket.save()
            ticketRow = TicketOperationTable(user_id=request.user.id, ticket_id=ticket.id, operation_flag=1)
            ticketRow.save()
            return redirect('http://127.0.0.1:8000/done_tickets/')
        elif (val == "2"):  # Rejected
            ticket.operation_flag = int(val)
            ticket.status_flag = 1
            ticket.save()
            ticketRow = TicketOperationTable(user_id=request.user.id, ticket_id=ticket.id, operation_flag=2)
            ticketRow.save()
            return redirect('http://127.0.0.1:8000/done_tickets/')
        elif (val == "0"):  # Don't Change
            ticket.operation_flag = int(val)
            ticket.status_flag = 0
            ticket.save()
            ticketRow = TicketOperationTable(user_id=request.user.id, ticket_id=ticket.id, operation_flag=0)
            ticketRow.save()
            return redirect('http://127.0.0.1:8000/done_tickets/')
        else:
            ticket.operation_flag = int(val)
            ticket.status_flag = 0
            ticket.save()
            return redirect('http://127.0.0.1:8000/done_tickets/')
    # --------------------------------------------

    context = {
        'ticket_list': ticket_list,
    }

    return render(request, "home/ui-tables-done.html", context)


@login_required()
def refreshWaitingTable(request):
    global globalPage
    global globalID

    myuser = request.user


    # Paginator-----------------------------------
    page_num = int(request.GET.get('pg_num') or myuser.account.per_page)
    myuser.account.per_page = page_num
    myuser.account.save()
    # --------------------------------------------


    if request.user.groups.filter(name="bug_report"):
        ticket_list1 = TicketDataTable.objects.filter(operation_flag=0, subject="Bug Report")
    else:
        ticket_list1 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="false_positive"):
        ticket_list2 = TicketDataTable.objects.filter(operation_flag=0, subject="False Positive")
    else:
        ticket_list2 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="suggestions"):
        ticket_list3 = TicketDataTable.objects.filter(operation_flag=0, subject="Suggestion & Ideas")
    else:
        ticket_list3 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="academic"):
        ticket_list4 = TicketDataTable.objects.filter(operation_flag=0, subject="Academic Request")
    else:
        ticket_list4 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="other"):
        ticket_list5 = TicketDataTable.objects.filter(operation_flag=0, subject="Other Topics")
    else:
        ticket_list5 = TicketDataTable.objects.none()

    temp_list = ticket_list1 | ticket_list2 | ticket_list3 | ticket_list4 | ticket_list5

    new_list = temp_list.filter(domain__contains=filter_domain,
                                    fullname__icontains=filter_name,
                                    email__startswith=filter_email,
                                    subject__startswith=filter_subject)
    p = Paginator(new_list.order_by("-date_created").values(), myuser.account.per_page)
    ticket_list = p.get_page(globalPage)


    context = {
        'ticket_list': ticket_list,
    }
    return render(request, "home/refreshWaitTable.html", context)


@login_required()
def refreshDoneTable(request):
    global globalPage
    global globalID

    myuser = request.user

    # Paginator-----------------------------------
    page_num = int(request.GET.get('pg_num') or myuser.account.per_page)
    myuser.account.per_page = page_num
    myuser.account.save()
    # --------------------------------------------

    # User verification--> Users can only see subject that they are assigned to
    if request.user.groups.filter(name="bug_report"):
        ticket_list1 = TicketDataTable.objects.filter(Q(operation_flag=1) | Q(operation_flag=2), subject="Bug Report")
    else:
        ticket_list1 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="false_positive"):
        ticket_list2 = TicketDataTable.objects.filter(Q(operation_flag=1) | Q(operation_flag=2), subject="False Positive")
    else:
        ticket_list2 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="suggestions"):
        ticket_list3 = TicketDataTable.objects.filter(Q(operation_flag=1) | Q(operation_flag=2), subject="Suggestion & Ideas")
    else:
        ticket_list3 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="academic"):
        ticket_list4 = TicketDataTable.objects.filter(Q(operation_flag=1) | Q(operation_flag=2), subject="Academic Request")
    else:
        ticket_list4 = TicketDataTable.objects.none()

    if request.user.groups.filter(name="other"):
        ticket_list5 = TicketDataTable.objects.filter(Q(operation_flag=1) | Q(operation_flag=2), subject="Other Topics")
    else:
        ticket_list5 = TicketDataTable.objects.none()

    temp_list = ticket_list1 | ticket_list2 | ticket_list3 | ticket_list4 | ticket_list5
    new_list = temp_list.filter(fullname__icontains=filter_name,
                                email__startswith=filter_email,
                                domain__contains=filter_domain,
                                subject__startswith=filter_subject,
                                operation_flag__startswith=filter_process)
    p = Paginator(new_list.order_by("-date_updated").values(), myuser.account.per_page)
    ticket_list = p.get_page(globalPage)
    # --------------------------------------------
    
    context = {
        'ticket_list': ticket_list,
    }
    return render(request, "home/refreshDoneTable.html", context)


# Creating a ticket internally
@login_required()
def createTicket(request):
    # Getting form data--------------------
    if request.method == 'POST':
        myuser = request.user
        firstname = myuser.first_name
        lastname = myuser.last_name
        email = myuser.email
        scenario = request.POST.get('scnr', False)
        subject = request.POST.get('sub_select', False)

        # finding domains in scenario---------------
        temp = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', scenario)

        # removing braces from temp object making domain pure string
        empty = ' '

        url = empty.join(temp)
        if url != "":
            if not ("https://" in url):
                temp2 = "https://"+url
                url = temp2

        myDomain = print(request.POST.get("domain"))

        if url != "":
            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Firefox(options=options, executable_path="./apps/home/geckodriver")
            driver.get(url)
            imgName = get_random_string(8)
            driver.save_screenshot("./apps/static/images/" + imgName + '.png')
            driver.quit()
            imgName += '.png'

            # Saving Ticket-------
            ticket = Ticket(firstname=firstname, lastname=lastname, email=email, scenario=scenario, subject=subject)
            ticket.save()

            fullname = ticket.firstname + " " + ticket.lastname
            tdt = TicketDataTable(fullname=fullname, email=ticket.email,
                                  subject=ticket.subject, scenario=ticket.scenario, operation_flag=Operations.get(0),
                                  status_flag=Status.get(0), domain=url, imageName=imgName)
            tdt.save()
        else:
            # Saving Ticket-------
            ticket = Ticket(firstname=firstname, lastname=lastname, email=email, scenario=scenario, subject=subject)
            ticket.save()

            fullname = ticket.firstname + " " + ticket.lastname
            tdt = TicketDataTable(fullname=fullname, email=ticket.email,
                                    subject=ticket.subject, scenario=ticket.scenario, operation_flag=Operations.get(0),
                                    status_flag=Status.get(0))
            tdt.save()

    return redirect(request.META['HTTP_REFERER'])

#endregion
#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*


#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
#region creating/fetching tickets
# Sends ticket data to client-side to render ticket to modal
@csrf_exempt
def getTicket(request, pk):
    ticket = TicketDataTable.objects.get(id=pk)  # gets ticket ID returns whole ticket
    ticket.status_flag = 2  # Whenever a ticket are being inspected by another user, this will lock others to reach to that ticket
    ticket.save()

    # creating a dictionary out of a model to send to the client-side
    dict_obj = model_to_dict(ticket)
    json_data = json.dumps(dict_obj)
    json_without_slash = json.loads(json_data)
    html_file_name = get_random_string(8)

    data = {
        'id': json_without_slash,
        'imageName': ticket.imageName,
    }
    return JsonResponse(data)

#-------------------------------------------------------------
#region handling json input from client
class Payload(object):

    def __init__(self, j):
        self.__dict__ = json.loads(j)


@api_view(['POST'])
@csrf_exempt
def pend(request):
    if (request.body != None):
        p = Payload(request.body)

    ticket = Ticket(firstname=p.firstname, lastname=p.lastname, email=p.email, subject=p.subjects, scenario=p.scenario)
    ticket.save()

    temp = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', scenario)

    empty = ' '
    url = empty.join(temp)
    
    if url != "":
        if not ("https://" in url):
            temp2 = "https://"+url
            url = temp2

    myDomain = request.POST.get("domain")

    if url != "":
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options, executable_path="./apps/home/geckodriver")
        driver.get(url)
        imgName = get_random_string(8)
        driver.save_screenshot("./apps/static/images/" + imgName + '.png')
        driver.quit()
        imgName += '.png'

        # Saving Ticket-------
        fullname = ticket.firstname + " " + ticket.lastname
        tdt = TicketDataTable(fullname=fullname, email=ticket.email,
                                subject=ticket.subject, scenario=ticket.scenario, operation_flag=Operations.get(0),
                                status_flag=Status.get(0), domain=url, imageName=imgName)
        tdt.save()
    else:
        # Saving Ticket-------
        tdt = TicketDataTable(firstname=ticket.firstname, lastname=ticket.lastname, email=ticket.email,
                                subject=ticket.subject, scenario=ticket.scenario, operation_flag=Operations.get(0),
                                status_flag=Status.get(0))
        tdt.save()
    return Response()

#endregion
#-------------------------------------------------------------

#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
#endregion
#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*



#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
#region adminDashboard

@csrf_exempt
def setDates(request):
    global startDate
    global endDate
    global dateOption
    global userChartID
    if request.method == 'POST':
        if request.is_ajax():
            startDate = request.POST.get("start")
            endDate = request.POST.get("end")
            print()
            print(startDate)
            print(endDate)
            print()
        else :
            option = request.POST.get("dateOption")
            userChartID = request.POST.get("userID")
            if int(option) == 1:
                dateOption = 0
            elif int(option) == 2:
                dateOption = 1
            elif int(option) == 3:
                dateOption = 2
            return redirect("http://127.0.0.1:8000/adminDashboard/")
    return redirect("http://127.0.0.1:8000/adminDashboard/")


@csrf_exempt
def monthChart(request):

    global startDate
    global endDate
    global dateOption
    global userChartID
    startDateStripped = datetime.datetime.strptime(startDate, "%Y-%m-%d")
    endDateStripped = datetime.datetime.strptime(endDate, "%Y-%m-%d")

    #region Creating_Dictionaries
    #Creating dictionaries keys-> months values -> count-------------------------------------
    #region MONTHS
    months = {'JAN' : 0, "FEB" : 0, "MAR" : 0, "APR" : 0, "MAY" : 0, "JUN" : 0, "JUL" : 0,
        "AUG" : 0, "SEP" : 0, "OCT" : 0, "NOV" : 0, "DEC" : 0}

    monthsCleaned = {'JAN' : 0, "FEB" : 0, "MAR" : 0, "APR" : 0, "MAY" : 0, "JUN" : 0, "JUL" : 0,
        "AUG" : 0, "SEP" : 0, "OCT" : 0, "NOV" : 0, "DEC" : 0}

    monthsRejected = {'JAN' : 0, "FEB" : 0, "MAR" : 0, "APR" : 0, "MAY" : 0, "JUN" : 0, "JUL" : 0,
        "AUG" : 0, "SEP" : 0, "OCT" : 0, "NOV" : 0, "DEC" : 0}
    
    userMonths = {'JAN' : 0, "FEB" : 0, "MAR" : 0, "APR" : 0, "MAY" : 0, "JUN" : 0, "JUL" : 0,
        "AUG" : 0, "SEP" : 0, "OCT" : 0, "NOV" : 0, "DEC" : 0}
    #endregion

    #region DAYS
    j = 0
    dayKeys = []
    dayValues = []
    days ={}
    daysCleaned = {}
    daysRejected ={}
    userDays = {}
    howManyDay = endDateStripped-startDateStripped

    if(dateOption != 2):
        if (howManyDay > timedelta(days = 40)):
            dateOption = 1

    daysStart = {}
    daysEnd = {}
    userDaysStart = {}
    userDaysEnd = {}
    dayStartKeys = []
    dayStartValues = []
    dayEndKeys = []
    dayEndValues = []
    daysStartCleaned = {}
    daysEndCleaned = {}
    daysStartRejected = {}
    daysEndRejected = {}
    if(endDateStripped.month > startDateStripped.month):
       
        startMonthDayCount = calendar.monthrange(startDateStripped.year, startDateStripped.month)[1]
        endMonthDayCount = calendar.monthrange(endDateStripped.year, endDateStripped.month)[1]

        for i in range(startDateStripped.day, startMonthDayCount + 1):
            dayStartKeys.append(str(i))
            dayStartValues.append(0)

        for i in range(1, endDateStripped.day + 1):
            dayEndKeys.append(str(i))
            dayEndValues.append(0)

        daysStart = dict(zip(dayStartKeys, dayStartValues))
        daysEnd = dict(zip(dayEndKeys,dayEndValues))
        daysStartCleaned = dict(zip(dayStartKeys, dayStartValues))
        daysEndCleaned = dict(zip(dayEndKeys, dayEndValues))
        daysStartRejected = dict(zip(dayStartKeys, dayStartValues))
        daysEndRejected = dict(zip(dayEndKeys, dayEndValues))
        userDaysStart = dict(zip(dayStartKeys, dayStartValues))
        userDaysEnd = dict(zip(dayEndKeys, dayEndValues))
    else:
        dayMonth = (endDateStripped.month - startDateStripped.month) * 30
        totalDays = dayMonth + endDateStripped.day - startDateStripped.day
        for i in range(startDateStripped.day, endDateStripped.day + 1):
            dayKeys.append(str(i))
            dayValues.append(0)
            j+=1

        days = dict(zip(dayKeys, dayValues))
        userDays = dict(zip(dayKeys, dayValues))
        daysCleaned = dict(zip(dayKeys, dayValues))
        daysRejected = dict(zip(dayKeys, dayValues))


    #endregion

    #region YEARS
    j = 0
    yearKeys = []
    yearValues = []
    userYears = {}
    for i in range(startDateStripped.year, endDateStripped.year + 1):
        yearKeys.append(str(i))
        yearValues.append(0)
        j+=1

    years = dict(zip(yearKeys, yearValues))
    userYears = dict(zip(dayKeys, dayValues))
    yearsCleaned = dict(zip(yearKeys, yearValues))
    yearsRejected = dict(zip(yearKeys, yearValues))
    #endregion
    #----------------------------------------------------------------------------------------
    #endregion


    if int(dateOption) == 2:

        #region yearly_calculation
        if(endDateStripped.year > startDateStripped.year):

            
            i = startDateStripped.year
            for year in years:
                years[year] = TicketDataTable.objects.filter(date_created__year = i).count()
                i+=1
            
            i = startDateStripped.year
            for year in userYears:
                userYears[year] = TicketOperationTable.objects.filter(date__year = i, user_id = userChartID).count()
                i+=1

            i = startDateStripped.year
            for year in yearsCleaned:
                yearsCleaned[year] = TicketOperationTable.objects.filter(date__year = i, operation_flag = 1).count()
                i+=1

            i = startDateStripped.year
            for year in yearsRejected:
                yearsRejected[year] = TicketOperationTable.objects.filter(date__year = i, operation_flag = 2).count()
                i+=1
            data = {
                "dict" : years,
                "userDict" : userYears,
                "dictCleaned" : yearsCleaned,
                "dictRejected" : yearsRejected,
                "time" : 0, #Deciding what to write on UI (year)
                "start" : startDate,
                "end" : endDate,
            }
            return JsonResponse(data)
        #endregion
    
    elif int(dateOption) == 1:
        #region monthly_calculation
            i = 1 #for total number of recieved tickets
            for month in months:
                months[month] = TicketDataTable.objects.filter(date_created__year = startDateStripped.year, date_created__month = i).count()
                i += 1
            
            i = 1 #for total number of recieved tickets
            for month in userMonths:
                userMonths[month] = TicketOperationTable.objects.filter(date__year = startDateStripped.year, date__month = i, user_id = userChartID).count()
                i += 1

            i = 1 #for cleaned tickets
            for month in monthsCleaned:
                monthsCleaned[month] = TicketOperationTable.objects.filter(date__year = startDateStripped.year, date__month = i, operation_flag = 1).count()
                i += 1

            i = 1 #for rejected tickets
            for month in monthsRejected:
                monthsRejected[month] = TicketOperationTable.objects.filter(date__year = startDateStripped.year, date__month = i, operation_flag = 2).count()
                i += 1

            data = {
                "dict" : months,
                "userDict" : userMonths,
                "dictCleaned" : monthsCleaned,
                "dictRejected" : monthsRejected,
                "time" : 1, #Deciding what to write on UI (month)
                "start" : startDate,
                "end" : endDate,
            }
            return JsonResponse(data)
            #endregion
    
    elif int(dateOption) == 0:

        if(endDateStripped.month == startDateStripped.month):

            #region daily_calculation
            i = startDateStripped.day #for total number of recieved tickets
            for day in days:
                days[day] = TicketDataTable.objects.filter(date_created__year = startDateStripped.year, date_created__month = startDateStripped.month,
                date_created__day = i).count()
                i += 1
            
            i = startDateStripped.day #for total number of recieved tickets
            for day in userDays:
                userDays[day] = TicketOperationTable.objects.filter(date__year = startDateStripped.year, date__month = startDateStripped.month,
                date__day = i, user_id = userChartID).count()
                i += 1

            i = startDateStripped.day #for cleaned tickets
            for day in daysCleaned:
                daysCleaned[day] = TicketOperationTable.objects.filter(date__year = startDateStripped.year, date__month = startDateStripped.month,
                    operation_flag = 1,  date__day = i).count()
                i += 1

            i = startDateStripped.day #for rejected tickets
            for day in daysRejected:
                daysRejected[day] = TicketOperationTable.objects.filter(date__year = startDateStripped.year, date__month = startDateStripped.month,
                    operation_flag = 2, date__day = i).count()
                i += 1
            #endregion

            data = {
                "dict" : days,
                "userDict" : userDays,
                "dictCleaned" : daysCleaned,
                "dictRejected" : daysRejected,
                "time" : 2, #Deciding what to write on UI (day)
                "start" : startDate,
                "end" : endDate,
            }
            return JsonResponse(data)
        elif(endDateStripped.month != startDateStripped.month):

            
            #region daily_calculation
            
            #region total
            i = startDateStripped.day #for total number of recieved tickets
            for day in daysStart:
                daysStart[day] = TicketDataTable.objects.filter(date_created__year = startDateStripped.year, date_created__month = startDateStripped.month,
                date_created__day = i).count()
                if (i == calendar.monthrange(startDateStripped.year, startDateStripped.month)[1] + 1):
                    break
                i += 1

            
            i = 1
            for day in daysEnd : 
                daysEnd[str(i)] = TicketDataTable.objects.filter(date_created__year = endDateStripped.year, date_created__month = endDateStripped.month,
                date_created__day = i).count()
                print(i)
                i += 1
                if(i == endDateStripped.day +1):
                    break

            i = startDateStripped.day #for total number of recieved tickets
            for day in userDaysStart:
                userDaysStart[day] = TicketOperationTable.objects.filter(date__year = startDateStripped.year, date__month = startDateStripped.month,
                date__day = i, user_id = userChartID).count()
                if (i == calendar.monthrange(startDateStripped.year, startDateStripped.month)[1] + 1):
                    break
                i += 1

            print()
            print(userDaysStart)
            print()
            i = 1
            for day in userDaysEnd : 
                userDaysEnd[str(i)] = TicketOperationTable.objects.filter(date__year = endDateStripped.year, date__month = endDateStripped.month,
                date__day = i, user_id = userChartID).count()
                print(i)
                i += 1
                if(i == endDateStripped.day +1):
                    break
            print()
            print(userDaysStart)
            print()
            #endregion
            
            #region cleaned
            i = startDateStripped.day #for total number of recieved tickets
            for day in daysStartCleaned:
                daysStartCleaned[day] = TicketOperationTable.objects.filter(date__year = startDateStripped.year, date__month = startDateStripped.month,
                    operation_flag = 1, date__day = i).count()
                if (i == calendar.monthrange(startDateStripped.year, startDateStripped.month)[1] + 1):
                    break
                i += 1


            i = 1
            for day in daysEndCleaned : 
                daysEndCleaned[str(i)] = TicketOperationTable.objects.filter(date__year = endDateStripped.year, date__month = endDateStripped.month,
                    operation_flag = 1, date__day = i).count()
                i += 1
                if(i == endDateStripped.day +1):
                    break
            #endregion 
            
            #region reject
            i = startDateStripped.day #for total number of recieved tickets
            for day in daysStartRejected:
                daysStartRejected[day] = TicketOperationTable.objects.filter(date__year = startDateStripped.year, date__month = startDateStripped.month,
                    operation_flag = 2, date__day = i).count()
                if (i == calendar.monthrange(startDateStripped.year, startDateStripped.month)[1] + 1):
                    break
                i += 1

            i = 1 #for total number of recieved tickets
            for day in daysEndRejected:
                daysEndRejected[str(i)] = TicketOperationTable.objects.filter(date__year = endDateStripped.year, date__month = endDateStripped.month,
                    operation_flag = 2, date__day = i).count()
                if(i == endDateStripped.day +1):
                    break
                i += 1
            #endregion
            #endregion

            data = {
                "option" : 1,
                "dayStart" : daysStart,
                "dayEnd" : daysEnd,
                "userStart" : userDaysStart,
                "userEnd" : userDaysEnd,
                "dayStartCleaned" : daysStartCleaned,
                "dayEndCleaned" : daysEndCleaned,
                "dayStartRejected" : daysStartRejected,
                "dayEndRejected" : daysEndRejected,
                "time" : 2, #Deciding what to write on UI (daily)
                "start" : startDate,
                "end" : endDate,
            }
            return JsonResponse(data)


    data = {
        "dict" : months,
        "dictCleaned" : monthsCleaned,
        "dictRejected" : monthsRejected,
        "start" : startDate,
        "end" : endDate,
    }
    return JsonResponse(data)


@login_required()
def adminDashboard(request):
    allUsers = User.objects.all()

    context = {
        "users" : allUsers,
    }
    return render(request, "home/adminDashboard.html", context)


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str


userChartID = 1
@csrf_exempt
def setUserID(request):
    global userChartID
    if (request.method == 'POST'):
        userChartID = request.POST.get("userID")
        return redirect("http://127.0.0.1:8000/adminDashboard/")
    return redirect("http://127.0.0.1:8000/adminDashboard/")

@csrf_exempt
def userChart(request):
    global userChartID
    print()
    print(userChartID)
    print()
    months = {'JAN' : 0, "FEB" : 0, "MAR" : 0, "APR" : 0, "MAY" : 0, "JUN" : 0, "JUL" : 0,
        "AUG" : 0, "SEP" : 0, "OCT" : 0, "NOV" : 0, "DEC" : 0}

    monthsCleaned = {'JAN' : 0, "FEB" : 0, "MAR" : 0, "APR" : 0, "MAY" : 0, "JUN" : 0, "JUL" : 0,
        "AUG" : 0, "SEP" : 0, "OCT" : 0, "NOV" : 0, "DEC" : 0}

    monthsRejected = {'JAN' : 0, "FEB" : 0, "MAR" : 0, "APR" : 0, "MAY" : 0, "JUN" : 0, "JUL" : 0,
        "AUG" : 0, "SEP" : 0, "OCT" : 0, "NOV" : 0, "DEC" : 0}
        

    if (request.method == 'GET'):
        i = 1 #for total number of recieved tickets
        for month in months:
            months[month] = TicketOperationTable.objects.filter(user_id = userChartID, date__year = date.today().year, date__month = i).count()
            i += 1
        obj = User.objects.get(id = userChartID)
        data = {
            "id" : userChartID,
            "fname" : obj.first_name,
            "lname" : obj.last_name,
            "months" : months,
        }
        return JsonResponse(data)
    
    data = {
        "months" : months,
    }
    return JsonResponse(data)

#endregion
#*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*