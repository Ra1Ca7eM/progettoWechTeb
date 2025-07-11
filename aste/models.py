from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# - `django.db.models`: Questo è il modulo che contiene la classe base `models.Model`
#   e tutti i tipi di campo (CharField, IntegerField, etc.) che useremo.
# - `django.contrib.auth.models.User`: Importiamo il modello User predefinito di Django.
#   Lo useremo per collegare aste, offerte e feedback a utenti specifici.
#   `django.contrib.auth` è l'app di autenticazione integrata.

class Profile(models.Model):
    # Questa classe estende le informazioni dell'utente standard di Django.
    
    # Crea una relazione uno-a-uno con il modello User.
    # `on_delete=models.CASCADE` significa che se un User viene cancellato,
    # anche il suo profilo associato verrà cancellato.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Definiamo le scelte possibili per il ruolo.
    # È una lista di tuple. Il primo elemento di ogni tupla è il valore salvato nel DB,
    # il secondo è il nome visualizzato all'utente.
    RUOLI = (
        ('acquirente', 'Acquirente'),
        ('venditore', 'Venditore'),
    )
    
    # `CharField` è un campo per stringhe di testo.
    # `max_length` è obbligatorio.
    # `choices` limita i valori possibili a quelli definiti in RUOLI.
    # `default` imposta un valore predefinito.
    ruolo = models.CharField(max_length=10, choices=RUOLI, default='acquirente')

    def __str__(self):
        # Il metodo `__str__` definisce come un oggetto verrà rappresentato
        # come stringa (ad esempio, nell'interfaccia di admin). È una buona pratica
        # definirlo per ogni modello.
        return f"Profilo di {self.user.username} - Ruolo: {self.get_ruolo_display()}"
    

class Categoria(models.Model):
    # Un modello semplice per le categorie dei prodotti.
    nome = models.CharField(max_length=100, unique=True) # `unique=True` assicura che non ci siano categorie con lo stesso nome.

    class Meta:
        # La classe Meta interna permette di configurare metadati del modello.
        # `verbose_name_plural` definisce come il modello verrà chiamato al plurale nell'admin.
        verbose_name_plural = "Categorie"

    def __str__(self):
        return self.nome
    
class AstaManager(models.Manager):
    def get_aste_vinte(self, user):
        # Spiegazione: Questo metodo personalizzato trova tutte le aste vinte da un utente.
        # 1. Filtra le aste il cui stato è 'conclusa'.
        aste_concluse = self.filter(stato='conclusa')
        
        # 2. Trova gli ID delle aste dove l'offerta più alta appartiene all'utente.
        aste_vinte_ids = [
            asta.id for asta in aste_concluse 
            if asta.offerte.first() and asta.offerte.first().acquirente == user
        ]
        
        # 3. Restituisce il queryset finale.
        return self.filter(pk__in=aste_vinte_ids)

class Asta(models.Model):
    # Il cuore del nostro sistema.
    
    # Relazione molti-a-uno (ForeignKey) con il modello User. Ogni asta ha un solo venditore.
    # `related_name='aste_create'` ci permetterà di accedere a tutte le aste di un utente
    # con `user.aste_create.all()`.
    venditore = models.ForeignKey(User, on_delete=models.CASCADE, related_name='aste_create')
    
    titolo = models.CharField(max_length=200)
    descrizione = models.TextField() # `TextField` è per testi lunghi, senza un limite di lunghezza.
    
    # `upload_to='aste_images/'` dice a Django di salvare le immagini caricate
    # in una sottocartella `aste_images` dentro la nostra cartella di file media (che configureremo).
    immagine = models.ImageField(upload_to='aste_images/')
    
    # Relazione molti-a-uno con Categoria.
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    # `on_delete=models.SET_NULL` e `null=True`: se una categoria viene cancellata,
    # il campo categoria di quest'asta diventa NULL, ma l'asta non viene cancellata.
    
    prezzo_base = models.DecimalField(max_digits=10, decimal_places=2) # `DecimalField` è ideale per i soldi.
    rilancio_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    
    data_inizio = models.DateTimeField(auto_now_add=True) # `auto_now_add=True` imposta la data e ora correnti solo alla creazione dell'oggetto.
    data_fine = models.DateTimeField()
    
    # Definiamo gli stati possibili dell'asta.
    STATI = (
        ('attiva', 'Attiva'),
        ('conclusa', 'Conclusa'),
        ('annullata', 'Annullata'),
    )
    stato = models.CharField(max_length=10, choices=STATI, default='attiva')
    
    # `ManyToManyField` per la lista dei desideri. Un utente può avere molte aste preferite,
    # e un'asta può essere nei preferiti di molti utenti.
    # `blank=True` significa che questo campo non è obbligatorio.
    utenti_lista_desideri = models.ManyToManyField(User, related_name='lista_desideri', blank=True)
    objects = AstaManager()
    class Meta:
        verbose_name_plural = "Aste"

    def __str__(self):
        return f"Asta: {self.titolo} | Venditore: {self.venditore.username}"
    
    def aggiorna_stato_se_scaduta(self):
        # Spiegazione: Questo metodo controlla se l'asta è scaduta e non è già conclusa.
        if self.stato == 'attiva' and self.data_fine < timezone.now():
            self.stato = 'conclusa'
            self.save() # Salva la modifica nel database
            # Restituisce True se lo stato è cambiato, altrimenti False.
            return True
        return False
    
class Offerta(models.Model):
    # Rappresenta un singolo rilancio su un'asta.
    
    asta = models.ForeignKey(Asta, on_delete=models.CASCADE, related_name='offerte')
    acquirente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offerte_fatte')
    importo = models.DecimalField(max_digits=10, decimal_places=2)
    data_offerta = models.DateTimeField(auto_now_add=True)

    class Meta:
        # `unique_together` garantisce che la combinazione di asta e importo sia unica,
        # prevenendo offerte duplicate dello stesso valore sulla stessa asta.
        unique_together = ('asta', 'importo')
        ordering = ['-importo'] # Ordina le offerte dalla più alta alla più bassa di default.
        verbose_name_plural = "Offerte"

    def __str__(self):
        return f"Offerta di {self.importo} su '{self.asta.titolo}' da {self.acquirente.username}"

class Feedback(models.Model):
    # Modello per le recensioni.
    
    asta = models.ForeignKey(Asta, on_delete=models.CASCADE, related_name='feedback')
    autore = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_dati')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_ricevuti')
    voto = models.PositiveIntegerField() # Un intero che può essere solo >= 0.
    commento = models.TextField()
    data_creazione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback da {self.autore.username} a {self.destinatario.username} per '{self.asta.titolo}'"
    
    

