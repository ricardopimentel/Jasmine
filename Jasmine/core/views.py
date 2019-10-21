import datetime
from django.db.models import Sum
from django.shortcuts import render, resolve_url as r, redirect

from Jasmine.core.models import jobs_log

def home(request, user_u, printer_u, host_u):
    hoje = datetime.datetime.today()

    user_data_inicial = datetime.datetime.fromordinal(hoje.toordinal() - int(user_u))
    printer_data_inicial = datetime.datetime.fromordinal(hoje.toordinal() - int(printer_u))
    host_data_inicial = datetime.datetime.fromordinal(hoje.toordinal() - int(host_u))

    request.session['user_u'] = user_u
    request.session['printer_u'] = printer_u
    request.session['host_u'] = host_u

    top_users = jobs_log.objects.filter(date__range=[user_data_inicial, hoje]).values('user').annotate(soma=Sum('pages')).order_by('-soma')[0:5]
    top_printers = jobs_log.objects.filter(date__range=[printer_data_inicial, hoje]).values('printer').annotate(soma=Sum('pages')).order_by('-soma')[0:5]
    top_hosts = jobs_log.objects.filter(date__range=[host_data_inicial, hoje]).values('host').annotate(soma=Sum('pages')).order_by('-soma')[0:5]

    # Preparando cores dos gráficos
    cores_primarias = ['#FF3035', '#46BFBD', '#FDB45C', '#512DA8', '#C2185B']
    cores_secundarias = ['#FF5A5E', '#5AD3D1', '#FFC870', '#673AB7', '#E91E63']

    return render(request, 'index.html', {
                       'title': 'Home',
                       'top_users': top_users,
                       'top_printers': top_printers,
                       'top_hosts': top_hosts,
                       'cores_primarias': cores_primarias,
                       'cores_secundarias': cores_secundarias,
                       'itemselec': 'HOME',
                     })


def redi(request):
    return redirect(r('home', user_u='30', printer_u='30', host_u='30'))
