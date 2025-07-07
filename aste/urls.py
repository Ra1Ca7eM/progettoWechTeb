from django.urls import path
from .views import *

# `app_name` definisce il namespace per gli URL di questa app.
# Ci permette di usare `{% url 'aste:nome_url' %}` nei template.
app_name = 'aste'

urlpatterns = [
    # La stringa vuota '' corrisponde alla root dell'app (che sarà / come definito nel file urls.py principale)
    path('', HomeAsteView.as_view(), name='home'),
    # Aggiungeremo l'URL per il dettaglio tra un attimo
    # Spiegazione: Questo è un path dinamico.
    # `<int:pk>` è un "path converter". Dice a Django di aspettarsi in questa
    # parte dell'URL un intero (`int`) e di passarlo alla vista
    # come un argomento chiamato `pk` (primary key).
    path('asta/<int:pk>/', DettaglioAstaView.as_view(), name='dettaglio_asta'),
]