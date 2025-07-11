
from django.urls import re_path # Usiamo re_path per i pattern regex degli URL
from . import consumers # Importa i tuoi consumer (che creeremo tra poco)

# Definisci le URL patterns per le connessioni WebSocket
websocket_urlpatterns = [
    # Questo pattern associa le connessioni WebSocket del tipo ws/asta/<id_asta>/
    # al nostro AstaConsumer.
    # (?P<pk>\d+) cattura l'ID dell'asta e lo passa al consumer come 'pk'.
    re_path(r'ws/asta/(?P<pk>\d+)/$', consumers.AstaConsumer.as_asgi()),
]