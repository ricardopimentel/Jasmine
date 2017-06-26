from django.db import connection
from django.shortcuts import render

def home(request):
    cursor = connection.cursor()
    cursor.execute("SELECT user, SUM(pages) as total FROM core_jobs_log GROUP BY user HAVING total >= 0 ORDER BY total DESC LIMIT 5")
    top_users = cursor.fetchall()
    cursor.execute("SELECT printer, SUM(pages) as total FROM core_jobs_log GROUP BY printer HAVING total >= 0 ORDER BY total DESC LIMIT 5")
    top_printers = cursor.fetchall()
    cursor.execute("SELECT host, SUM(pages) as total FROM core_jobs_log GROUP BY host HAVING total >= 0 ORDER BY total DESC LIMIT 5")
    top_hosts = cursor.fetchall()
    
    # Preparando cores dos gráficos
    cores_primarias = ['#F746A', '#46BFBD', '#FDB45C', '#512DA8', '#C2185B']
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