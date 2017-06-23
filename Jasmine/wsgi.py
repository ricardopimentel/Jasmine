"""
WSGI config for Jasmine project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
<<<<<<< HEAD
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
=======
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
>>>>>>> 9f532b12397d6ffd69bb2e8939b5ca4087275bcd
"""

import os

from django.core.wsgi import get_wsgi_application

<<<<<<< HEAD
=======

>>>>>>> 9f532b12397d6ffd69bb2e8939b5ca4087275bcd
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Jasmine.settings")

application = get_wsgi_application()
