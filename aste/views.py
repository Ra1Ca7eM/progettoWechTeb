from django.shortcuts import render
from django.views.generic import *
from .models import * 
from django.urls import reverse_lazy
from .forms import * # Importa il nostro nuovo form

class HomeAsteView(ListView):
    # Spiegazione: Stiamo creando una vista basata sulla generica ListView.

    # 1. Specifichiamo quale modello deve essere interrogato.
    #    Django eseguirà `Asta.objects.all()` per noi.
    model = Asta

    # 2. Specifichiamo quale template usare per mostrare i dati.
    template_name = 'aste/home.html'

    # 3. Di default, ListView passa la lista di oggetti al template
    #    in una variabile chiamata `object_list`. Le diamo un nome più chiaro.
    context_object_name = 'aste_list'

    def get_queryset(self):
        # Spiegazione: Stiamo sovrascrivendo il metodo `get_queryset`.
        # Invece di prendere TUTTE le aste (`Asta.objects.all()`),
        # prendiamo solo quelle 'attive' e le ordiniamo per data di fine.
        return Asta.objects.filter(stato='attiva').order_by('data_fine')
    

class DettaglioAstaView(DetailView):
    # Spiegazione: Questa vista è basata sulla generica DetailView.
    
    # 1. Specifichiamo il modello da cui pescare il singolo oggetto.
    model = Asta
    
    # 2. Specifichiamo il template da usare per mostrare i dettagli.
    template_name = 'aste/dettaglio_asta.html'
    
    # 3. Di default, DetailView passa l'oggetto al template in una variabile
    #    chiamata `object`. Le diamo un nome più chiaro e intuitivo.
    context_object_name = 'asta'

    def get_context_data(self, **kwargs):
        # Spiegazione: Stiamo sovrascrivendo questo metodo per aggiungere
        # più informazioni (il "contesto") da passare al template.
        # Oltre ai dettagli dell'asta, vogliamo anche mostrare la sua offerta più alta.

        # Chiamiamo prima l'implementazione base per ottenere il contesto di default
        context = super().get_context_data(**kwargs)
        
        # Recuperiamo l'offerta più alta per l'asta corrente.
        # `self.get_object()` ci dà l'istanza dell'asta che la vista sta mostrando.
        # Usiamo `first()` perché abbiamo ordinato le offerte in modo decrescente nel modello.
        offerta_piu_alta = self.get_object().offerte.first()
        
        # Aggiungiamo l'offerta al contesto che passeremo al template.
        context['offerta_piu_alta'] = offerta_piu_alta
        
        return context
    
class RegistrazioneView(CreateView):
    # Spiegazione: Usiamo una CreateView generica, ma la personalizziamo
    # per usare il nostro form invece di farne generare uno a Django.
    
    # 1. Invece di 'model', specifichiamo 'form_class'.
    #    Questo dice alla CreateView di usare il nostro CustomUserCreationForm.
    form_class = CustomUserCreationForm
    
    # 2. Specifichiamo il template che mostrerà il form.
    template_name = 'registration/registrazione.html'
    
    # 3. Specifichiamo l'URL a cui reindirizzare l'utente dopo una registrazione
    #    riuscita. `reverse_lazy` cerca un URL con il nome 'login'.
    success_url = reverse_lazy('login')