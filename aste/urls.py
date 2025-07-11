from django.urls import path
from django.contrib.auth import views as auth_views # Importiamo le viste di autenticazione di Django
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
    # URL per la registrazione
    path('registrazione/', RegistrazioneView.as_view(), name='registrazione'),
    
    # URL per il login e logout (usando le viste predefinite di Django)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    path('registrazione/completata/', RegistrazioneConfermaView.as_view(), name='registrazione_completata'),
    path('profilo/', ProfiloView.as_view(), name='profilo'),
    path('asta/nuova/', CreaAstaView.as_view(), name='crea_asta'),
    path('asta/<int:pk>/offerta/', fai_offerta, name='fai_offerta'),
    path('asta/<int:pk>/desideri/', gestisci_lista_desideri, name='gestisci_desideri'),
    path('asta/<int:pk>/feedback/', aggiungi_feedback, name='aggiungi_feedback'),
    path('ricerca/', RisultatiRicercaView.as_view(), name='ricerca'),
]