from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import * # Importiamo il nostro modello Profile

class CustomUserCreationForm(UserCreationForm):
    # Spiegazione: Stiamo estendendo il form di base per la creazione di utenti.

    # Aggiungiamo i campi che vogliamo nel nostro form di registrazione.
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email.')
    
    # Aggiungiamo il campo per la scelta del ruolo, prendendo le opzioni dal modello Profile.
    ruolo = forms.ChoiceField(choices=Profile.RUOLI, required=True)

    class Meta(UserCreationForm.Meta):
        # Specifichiamo che il nostro form è basato sul modello User
        # e includiamo i campi di default più i nostri.
        model = User
        fields = UserCreationForm.Meta.fields + ('username','first_name', 'last_name', 'email' )

    def save(self, commit=True):
        # Spiegazione: Stiamo sovrascrivendo il metodo save() del form.
        # Questo metodo viene chiamato quando il form è valido e deve salvare i dati.
        # Dobbiamo non solo salvare il nuovo User, ma anche creare e collegare il suo Profile.

        # 1. Salviamo l'utente (username, password, etc.) usando il metodo del genitore.
        user = super().save(commit=False) # commit=False per non salvarlo subito nel DB
        
        # 2. Impostiamo nome, cognome ed email dai dati "puliti" del form.
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save() # Ora salviamo l'utente.
            
            # 3. Creiamo il profilo associato.
            profile = Profile.objects.create(
                user=user,
                ruolo=self.cleaned_data["ruolo"]
            )
            profile.save()

        return user
    
    
class AstaForm(forms.ModelForm):
    # Spiegazione: Stiamo creando un form direttamente collegato al modello Asta.
    # Questo ci permette di non dover ridefinire i campi che esistono già nel modello.

    class Meta:
        # La classe Meta interna dice a Django come costruire il form.
        model = Asta
        
        # Specifichiamo quali campi del modello Asta devono apparire nel form.
        fields = ['titolo', 'descrizione', 'immagine', 'categoria', 'prezzo_base', 'rilancio_minimo', 'data_fine']

        # Spiegazione: Qui sta la magia! Il dizionario `widgets` ci permette di
        # sovrascrivere il widget di default per qualsiasi campo.
        widgets = {
            'data_fine': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local', # Questo dice al browser di usare il suo widget calendario nativo.
                    'class': 'form-control' # Aggiungiamo una classe Bootstrap per lo stile.
                }
            ),
            'descrizione': forms.Textarea(
                attrs={'rows': 4, 'class':'form-control'} # Rendiamo il campo descrizione un po' più grande.
            ),
        }
        
        
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        # L'utente compilerà solo questi due campi.
        # Gli altri (asta, autore, destinatario) li imposteremo noi nella vista.
        fields = ['voto', 'commento']
        widgets = {
            'voto': forms.HiddenInput(),
            'commento': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        
        
class SearchForm(forms.Form):
    # Spiegazione: Questo form non è legato a un modello, è un form generico
    # per raccogliere i parametri di ricerca dall'utente.
    
    keyword = forms.CharField(
        label='Parola chiave',
        required=False, # La ricerca può anche essere solo un filtro per categoria
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Es. Smartphone, libro antico...'})
    )

    categoria = forms.ModelChoiceField(
        label='Categoria',
        queryset=Categoria.objects.all(),
        required=False, # L'utente può non specificare una categoria
        empty_label="Tutte le categorie", # Testo per l'opzione vuota
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    includi_concluse = forms.BooleanField(
        label='Includi aste concluse',
        required=False # Di default, non le includiamo
    )

    # Creiamo le scelte per l'ordinamento
    ORDINA_PER_CHOICES = (
        ('data_fine', 'Tempo rimanente (più vicine alla scadenza)'),
        ('-data_fine', 'Tempo rimanente (più lontane dalla scadenza)'),
        ('prezzo_attuale', 'Prezzo (crescente)'),
        ('-prezzo_attuale', 'Prezzo (decrescente)'),
    )
    ordina_per = forms.ChoiceField(
        label='Ordina per',
        choices=ORDINA_PER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )