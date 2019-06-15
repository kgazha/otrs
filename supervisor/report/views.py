from django.shortcuts import render
from django.http import HttpResponse
from .models import Ticket


def index(request):
    tickets = Ticket.objects.all()
    print([x.verbose_name for x in Ticket._meta.get_fields()[1:] if x.verbose_name])
    context = {'fio': 'keka'}
    return render(request, 'report.html', context)
