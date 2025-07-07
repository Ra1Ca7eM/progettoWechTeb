from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile # Importiamo il nostro modello Profile

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
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

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