// Funzione standard per ottenere il token CSRF dai cookie.
// Ci servirà per tutte le nostre richieste POST.
document.addEventListener('DOMContentLoaded', function() {


    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Selettore per TUTTI i pulsanti "desideri", sia nella lista che nel dettaglio.
    const wishListButtons = document.querySelectorAll('.desideri-btn');

    wishListButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const astaId = this.dataset.astaId;
            const url = `/asta/${astaId}/desideri/`; // L'URL della nostra API view

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken // Usiamo il token preso dal cookie
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Aggiorniamo il pulsante cliccato
                    if (data.added) {
                        this.innerHTML = '♥';
                        this.classList.remove('btn-outline-danger');
                        this.classList.add('btn-danger');
                    } else {
                        this.innerHTML = '♡';
                        this.classList.remove('btn-danger');
                        this.classList.add('btn-outline-danger');
                    }
                }
            })
            .catch(error => console.error('Errore durante la richiesta desideri:', error));
        });
    });

    
    // Possiamo aggiungere qui anche lo script per le offerte
    const offertaForm = document.getElementById('offerta-form');

    if (offertaForm) {
        offertaForm.addEventListener('submit', function(event) {
            // Aggiungiamo un listener all'evento di submit del form
            // 1. Impediamo l'invio tradizionale del form, che ricaricherebbe la pagina
            event.preventDefault();

            // Leggiamo l'URL dall'attributo data-url che abbiamo messo nel form!
            const url = offertaForm.dataset.url; 
            
            const importo = offertaForm.querySelector('#importo-offerta').value;
            
            // 2. Usiamo l'API `fetch` per la nostra richiesta AJAX
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken // Token CSRF nell'header
                },
                body: JSON.stringify({ 'importo': importo }) // Inviamo i dati come stringa JSON
            })
            .then(response => response.json()) // 3. Attendiamo la risposta e la convertiamo in JSON
            .then(data => {
                // 4. Gestiamo la risposta del server
                const errorDiv = document.getElementById('error-message');
                if (data.success) {
                    // Successo! Aggiorniamo la pagina
                    errorDiv.style.display = 'none';
                    document.querySelector('#prezzo-attuale').innerHTML = `Prezzo attuale: € ${data.nuovo_prezzo}`;
                    document.querySelector('#acquirente-attuale').innerHTML = `<small>Offerta fatta da: ${data.acquirente}</small>`;
                    offertaForm.reset();
                } else {
                    // Errore! Mostriamo il messaggio di errore
                    errorDiv.textContent = data.error;
                    errorDiv.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Errore Fetch:', error);
            });
        });
    }




    const countdownElement = document.getElementById('countdown');
    
    // Eseguiamo questo codice solo se l'elemento del countdown esiste nella pagina
    if (countdownElement) {
         // Convertiamo la stringa ISO in un oggetto Date di JS
        const dataFineISO = countdownElement.dataset.fineAsta;
        const dataFine = new Date(dataFineISO);
        // Eseguiamo la funzione updateCountdown ogni secondo (1000 millisecondi)
        const timer = setInterval(function() {
            const adesso = new Date();
            const differenza = dataFine - adesso;

            if (differenza < 0) {
                return;
            }

            // Calcoliamo i giorni, ore, minuti e secondi rimanenti
            const giorni = Math.floor(differenza / (1000 * 60 * 60 * 24));
            const ore = Math.floor((differenza % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minuti = Math.floor((differenza % (1000 * 60 * 60)) / (1000 * 60));
            const secondi = Math.floor((differenza % (1000 * 60)) / 1000);

            // Componiamo la stringa da mostrare
            let output = "Scade tra: ";
            if (giorni > 0) output += giorni + "g ";
            if (ore > 0 || giorni > 0) output += ore + "h ";
            output += minuti + "m " + secondi + "s";

            // Aggiorniamo l'elemento HTML
            countdownElement.innerHTML = output;

        }, 1000);
    }




    const astaDetailContainer = document.getElementById('dettaglio-asta-container');
    
    // Questo codice viene eseguito solo se siamo sulla pagina di dettaglio di un'asta
    if (astaDetailContainer) {
        const astaId = astaDetailContainer.dataset.astaId;
        
        // Determina il protocollo WebSocket (ws:// per HTTP, wss:// per HTTPS)
        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        // Costruisci l'URL del WebSocket
        const socketUrl = protocol + window.location.host + '/ws/asta/' + astaId + '/';

        // Crea una nuova connessione WebSocket
        const astaSocket = new WebSocket(socketUrl);

        // Questo evento si scatena quando arriva un messaggio dal server tramite WebSocket
        astaSocket.onmessage = function(e) {
            const data = JSON.parse(e.data); // Il messaggio è una stringa JSON, convertila in oggetto JS
            
            // Aggiorna gli elementi HTML della pagina con i nuovi dati
            document.querySelector('#prezzo-attuale').innerHTML = `Prezzo attuale: € ${data.nuovo_prezzo}`;
            document.querySelector('#acquirente-attuale').innerHTML = `<small>Offerta fatta da: ${data.acquirente}</small>`;
            
            // Aggiungi un piccolo effetto visivo per notare l'aggiornamento
            const prezzoEl = document.querySelector('#prezzo-attuale');
            prezzoEl.style.transition = 'transform 0.2s ease-in-out';
            prezzoEl.style.transform = 'scale(1.1)';
            setTimeout(() => { prezzoEl.style.transform = 'scale(1)'; }, 200);
        };

        // Questo evento si scatena se la connessione WebSocket si chiude inaspettatamente
        astaSocket.onclose = function(e) {
            console.error('Socket dell\'asta chiuso inaspettatamente:', e);
        };
    }
    
});