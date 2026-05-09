# Socket Programming Exercises

Esercizi di programmazione con socket in Python (TCP e UDP).  
Ogni esercizio estende il precedente aggiungendo una funzionalità nuova.

---

## Struttura della repository

```
.
├── esercizio 0/
│   ├── tcp_client.py        # TCP client (base)
│   ├── tcp_server.py        # TCP server (base)
│   ├── udp_client.py        # UDP client (base)
│   └── udp_server.py        # UDP server (base)
├── esercizio 1/
│   ├── udp_server.py        # UDP server con contatore messaggi
│   └── udp_client.py        # UDP client che mostra il contatore
├── esercizio 2/
│   ├── tcp_server.py        # TCP server multi-client
│   └── tcp_client.py        # TCP client (invariato rispetto a Ex.0)
├── esercizio 3/
│   ├── udp_server.py        # UDP server con perdita pacchetti simulata
│   └── udp_client.py        # UDP client con gestione robusta del timeout
├── esercizio 4/
│   ├── kv_server.py         # Key-value store server (TCP)
│   └── kv_client.py         # Key-value store client (TCP)
└── README.md
```

---

## Come eseguire

Ogni esercizio richiede due terminali: uno per il server e uno per il client.  
Entra nella cartella dell'esercizio che vuoi provare, poi:

```bash
# Terminale 1
python tcp_server.py   # oppure udp_server.py / kv_server.py

# Terminale 2
python tcp_client.py   # oppure udp_client.py / kv_client.py
```

---

## Esercizio 0 — Refactoring con funzioni

**File:** `tcp_client.py`, `tcp_server.py`, `udp_client.py`, `udp_server.py`

Punto di partenza. Il codice originale aveva tutta la logica dentro `main()`. Il refactoring ha separato le responsabilità in funzioni distinte, estraendo i magic number come costanti.

### Modifiche comuni a tutti i file

| Cosa | Perché |
|------|--------|
| Magic number estratti come costanti (`NUM_PINGS`, `TIMEOUT_S`, ecc.) | Un solo posto dove cambiarli; il nome spiega il significato |
| `main()` ridotto a chiamate ad alto livello | `main()` descrive *cosa* fa il programma, le funzioni descrivono *come* |
| `try/finally` per la chiusura della socket | La socket viene chiusa anche in caso di eccezione imprevista |

### tcp_client.py

| Funzione | Cosa fa |
|----------|---------|
| `create_connection(host, port)` | Crea la socket e chiama `connect()` |
| `send_ping(sock, index)` | Incapsula `sendall()` + `recv()` per un singolo ping |
| `close_connection(sock)` | Teardown con log |

### tcp_server.py

| Funzione | Cosa fa |
|----------|---------|
| `create_server_socket(host, port)` | Create → `setsockopt` → `bind` → `listen` in un unico posto |
| `accept_client(server_sock)` | Wrapper su `accept()` con log — punto di intervento per Ex.2 |
| `build_reply(message)` | Logica applicativa pura, senza I/O di rete |
| `handle_client(conn)` | Loop di comunicazione con un singolo client — pronta per Ex.2 |

### udp_client.py

| Funzione | Cosa fa |
|----------|---------|
| `create_udp_socket(timeout)` | Crea la socket e imposta `settimeout()` |
| `send_ping(sock, host, port, index)` | Contiene il `try/except socket.timeout` — il loop in `main()` non è annidato |
| `close_socket(sock)` | Teardown |

### udp_server.py

| Funzione | Cosa fa |
|----------|---------|
| `create_udp_socket(host, port)` | Crea e lega la socket |
| `build_reply(message)` | Identica alla versione TCP: la logica non dipende dal protocollo |
| `receive_and_reply(sock)` | Un ciclo ricezione + risposta — punto di intervento per Ex.3 |
| `serve_forever(sock)` | Loop infinito che chiama `receive_and_reply()` |

---

## Esercizio 1 — Message Counter

**File:** `ex1_udp_server.py`, `ex1_udp_client.py`  
**Base:** file UDP di Ex.0

Il server conta i PING ricevuti e include il numero in ogni risposta (`PONG #1`, `PONG #2`, ...). Il client stampa la risposta completa.

### Dove vive il contatore?

È una variabile locale di `serve_forever()`, inizializzata a `0`:

```python
def serve_forever(sock):
    ping_count = 0
    while True:
        ping_count = receive_and_reply(sock, ping_count)
```

Viene passato a `receive_and_reply()` che lo incrementa e lo restituisce. Nessun globale, nessun side-effect nascosto.

**Se il server viene riavviato mentre il client è in esecuzione**, il contatore riparte da `1`: nuovo processo = nuova sessione.

### Modifiche rispetto a Ex.0

| File | Modifica |
|------|----------|
| `ex1_udp_server.py` | `build_reply(message, ping_count)` — aggiunto parametro, risposta diventa `f"PONG #{ping_count}"` |
| `ex1_udp_server.py` | `receive_and_reply(sock, ping_count) → int` — prende e restituisce il contatore |
| `ex1_udp_server.py` | `serve_forever` — `ping_count` aggiornato ad ogni iterazione col valore di ritorno |
| `ex1_udp_client.py` | `send_ping` — stampa `reply` (es. `"PONG #3"`) invece di un testo fisso |

---

## Esercizio 2 — Multi-client TCP Server

**File:** `tcp_server.py`, `tcp_client.py`  
**Base:** `tcp_server.py` di Ex.0  
**Client:** `tcp_client.py` è identico a quello di Ex.0, copiato nella cartella per completezza

Il server originale usciva dopo il primo client. Ora torna ad `accept()` dopo ogni disconnessione.

### Costanti configurabili

```python
MAX_CLIENTS = 3     # il server si ferma dopo aver servito N client
THREADED    = True  # False = sequenziale, True = un thread per client
```

### Modalità sequenziale (`THREADED = False`)

Il server gestisce un client alla volta. Dopo la disconnessione torna ad `accept()`.

### Modalità threaded (`THREADED = True`)

Ogni client viene gestito in un `Thread` separato. Il thread principale torna subito ad `accept()`, permettendo connessioni simultanee.

```python
t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
t.start()
```

`daemon=True` garantisce che i thread figli non blocchino l'uscita del processo quando `MAX_CLIENTS` è raggiunto.

> **Thread safety:** ogni thread ha la propria socket `conn`, non c'è stato condiviso tra thread, quindi non servono lock.

### Modifiche rispetto a Ex.0

| Modifica | Perché |
|----------|--------|
| `MAX_CLIENTS` al posto di un flag booleano | Criterio di terminazione deterministico, senza meccanismi esterni |
| `THREADED` come selettore di modalità | Basta cambiare un valore per confrontare le due modalità |
| Nuova funzione `accept_loop(server_sock)` | Contiene il loop su `accept()` — in sequenziale chiama `handle_client()` direttamente, in threaded spawna un `Thread` |
| `handle_client` riceve anche `addr` | In modalità threaded i log di client diversi si mescolano; `addr` identifica chi sta parlando |
| `listen(5)` invece di `listen(1)` | Con threading più handshake possono accumularsi in coda |

---

## Esercizio 3 — Unreliable Channel Simulation

**File:** `ex3_udp_server.py`, `ex3_udp_client.py`  
**Base:** file UDP di Ex.0

Su localhost i pacchetti UDP non si perdono mai. Il server simula la perdita con una probabilità configurabile, rendendo essenziale il timeout nel client.

### Costante configurabile

```python
DROP_PROBABILITY = 0.3  # 30% di probabilità di non inviare la risposta
```

### Come funziona il drop

```python
def should_drop() -> bool:
    return random.random() < DROP_PROBABILITY
```

Se `should_drop()` restituisce `True`, il server non chiama `sendto()` e stampa:
```
[Server] Dropped reply (simulated loss) → client vedrà timeout
```

### Modifiche rispetto a Ex.0

| File | Modifica |
|------|----------|
| `ex3_udp_server.py` | `DROP_PROBABILITY` come costante configurabile |
| `ex3_udp_server.py` | Nuova funzione `should_drop()` — isola la logica random, testabile con mock |
| `ex3_udp_server.py` | `receive_and_reply` — se `should_drop()` è `True`, salta `sendto()` |
| `ex3_udp_client.py` | `send_ping` restituisce `bool` (ricevuto/perso) |
| `ex3_udp_client.py` | Messaggio di timeout più descrittivo: `"Ping #N lost (server simulated drop or unreachable)"` |
| `ex3_udp_client.py` | Nuova funzione `print_summary(received, total)` — statistiche finali della sessione |

---

## Esercizio 4 — Key-Value Store (TCP)

**File:** `ex4_kv_server.py`, `ex4_kv_client.py`  
**Base:** file nuovi, non derivati dagli esercizi precedenti

### Scelte progettuali

**Protocollo: TCP**  
Un key-value store deve garantire che i comandi arrivino in ordine e che nessuno vada perso. Con UDP un `SET` potrebbe non arrivare e il client non lo saprebbe. TCP fornisce queste garanzie nativamente.

**Formato messaggi: testo piano, un comando per riga**

| Comando (client → server) | Risposta (server → client) |
|---------------------------|----------------------------|
| `SET <key> <value>` | `OK` |
| `GET <key>` | `VALUE <value>` oppure `NONE` |
| `DEL <key>` | `OK` |
| `KEYS` | `KEYS k1 k2 ...` |
| `QUIT` | `BYE` |
| comando malformato | `ERROR <motivo>` |

**Gestione errori:** il server risponde `ERROR <motivo>` senza chiudere la connessione. Il client può riprovare.

**Terminazione:** il client invia `QUIT`, il server risponde `BYE` e chiude `conn`. In alternativa il client può chiudere la socket direttamente (TCP FIN).

### Esempio di sessione

```
>>> SET nome Alice
    OK
>>> GET nome
    VALUE Alice
>>> GET eta
    NONE
>>> KEYS
    KEYS nome
>>> DEL nome
    OK
>>> QUIT
    BYE
```

### Struttura del server

`process_command(store, raw)` è una funzione pura (nessun I/O): tutta la logica applicativa in un posto, facile da testare e da estendere. Il server è multi-client via threading, riusando il pattern di Ex.2.

> **Nota:** ogni client ha il proprio store privato (dizionario locale in `handle_client`). In un sistema reale lo store sarebbe condiviso e protetto da lock.

---

## Principi applicati in tutti gli esercizi

- **Separazione delle responsabilità** — ogni funzione fa una sola cosa (setup socket / logica applicativa / loop di rete / teardown)
- **Nessun magic number inline** — tutte le costanti configurabili hanno un nome esplicito
- **`main()` ad alto livello** — non contiene logica di rete o applicativa
- **`try/finally` per il teardown** — le socket vengono chiuse anche su eccezioni impreviste
- **Nessuno stato globale mutato** — dove serve lo stato (contatore Ex.1), viene passato come parametro e restituito come valore di ritorno
- **Estensibilità verticale** — ogni esercizio modifica o aggiunge una singola funzione senza riscrivere le altre
