from django.db.models import Sum
from django.shortcuts import render
from Jasmine.core.models import jobs_log

def home(request):
    top_users = jobs_log.objects.values('user').annotate(soma=Sum('pages')).order_by('-soma')[0:5]
    top_printers = jobs_log.objects.values('printer').annotate(soma=Sum('pages')).order_by('-soma')[0:5]
    top_hosts = jobs_log.objects.values('host').annotate(soma=Sum('pages')).order_by('-soma')[0:5]

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