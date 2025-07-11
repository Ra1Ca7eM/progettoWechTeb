import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AstaConsumer(AsyncWebsocketConsumer):
    # Questo metodo viene chiamato quando un client si connette al WebSocket.
    async def connect(self):
        # Ottieni la chiave primaria (pk) dell'asta dall'URL del WebSocket.
        self.asta_pk = self.scope['url_route']['kwargs']['pk']
        # Crea un nome di gruppo univoco per questa asta (es. "asta_123").
        self.asta_group_name = f'asta_{self.asta_pk}'

        # Aggiungi questo canale (la connessione WebSocket corrente) al gruppo dell'asta.
        # Tutti i messaggi inviati a questo gruppo arriveranno qui.
        await self.channel_layer.group_add(
            self.asta_group_name,  # Il nome del gruppo a cui unirsi
            self.channel_name      # Il nome univoco del canale corrente
        )

        # Accetta la connessione WebSocket. Se non lo fai, la connessione verrà chiusa.
        await self.accept()

    # Questo metodo viene chiamato quando un client si disconnette dal WebSocket.
    async def disconnect(self, close_code):
        # Rimuovi questo canale dal gruppo dell'asta.
        await self.channel_layer.group_discard(
            self.asta_group_name,
            self.channel_name
        )

    # Questo metodo è un "ricevitore". Viene chiamato quando un messaggio
    # viene inviato al gruppo 'asta_X' con type: 'offerta.aggiornata'.
    async def offerta_aggiornata(self, event):
        # Estrai i dati dell'offerta dal messaggio ricevuto.
        dati_offerta = event['dati_offerta']
        
        # Invia questi dati come un messaggio JSON al client WebSocket.
        await self.send(text_data=json.dumps(dati_offerta))