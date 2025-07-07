from django.contrib import admin

# Importiamo tutti i modelli che abbiamo creato nel file models.py della stessa app.
from .models import Profile, Categoria, Asta, Offerta, Feedback

# Spiegazione:
# Il comando `admin.site.register()` è il modo con cui diciamo a Django:
# "Prendi questo modello e rendilo disponibile nell'interfaccia di amministrazione".
# Lo facciamo per ogni modello che vogliamo gestire.

admin.site.register(Profile)
admin.site.register(Categoria)
admin.site.register(Asta)
admin.site.register(Offerta)
admin.site.register(Feedback)