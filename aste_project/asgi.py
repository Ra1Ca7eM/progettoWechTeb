"""
ASGI config for aste_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""


import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import aste.routing # Importa il file di routing della tua app 'aste'

# Imposta la variabile d'ambiente per il modulo settings di Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aste_project.settings')

# L'oggetto 'application' è il punto di ingresso per il server ASGI
application = ProtocolTypeRouter({
    # Per le richieste HTTP normali (es. caricamento pagine, API REST)
    "http": get_asgi_application(),

    # Per le connessioni WebSocket
    "websocket": AuthMiddlewareStack( # Fornisce accesso all'utente autenticato
        URLRouter(
            aste.routing.websocket_urlpatterns # Le URL patterns specifiche per i WebSocket
        )
    ),
})