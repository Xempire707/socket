"""
Key-Value Store — Server (Exercise 4)

Author  : Pietro Boccadoro
Email   : pieroboccadoro13[at]gmail[dot]com
Date    : 2024-04-11
Version : 1.0  (Exercise 4 — custom messages exchange)

==============================================================================
DESIGN DOCUMENT (risposta alle domande dell'esercizio)
==============================================================================

Protocollo scelto: TCP
Motivazione:
  Un key-value store deve garantire che i comandi arrivino nell'ordine
  in cui sono stati inviati e che nessuno vada perso. Con UDP, un SET
  potrebbe non arrivare e il client non lo saprebbe; oppure un GET
  potrebbe arrivare prima del SET che lo precede logicamente.
  TCP fornisce queste garanzie nativamente senza implementare ACK manuali.

Formato dei messaggi (testo piano, un comando per riga):
  Client → Server:
    SET <key> <value>   →  imposta key=value
    GET <key>           →  legge il valore associato a key
    DEL <key>           →  elimina la chiave
    KEYS                →  elenca tutte le chiavi presenti
    QUIT                →  chiude la connessione

  Server → Client:
    OK                  →  SET / DEL riuscito
    VALUE <value>       →  risposta a GET (chiave trovata)
    NONE                →  risposta a GET (chiave non trovata)
    KEYS <k1> <k2> …    →  risposta a KEYS (spazio come separatore)
    ERROR <motivo>      →  comando non riconosciuto o malformato
    BYE                 →  risposta a QUIT prima di chiudere

Gestione messaggi malformati:
  Il server risponde ERROR <motivo> senza crashare.
  Esempi: "SET" senza argomenti → ERROR; "GET" con due argomenti → ERROR.

Condizione di terminazione:
  Il client invia QUIT; il server risponde BYE e chiude conn.
  In alternativa il client può chiudere la socket (TCP FIN) e il server
  uscirà dal loop su recv() vuoto.
  Il server stesso continua ad accettare nuovi client (multi-client come Ex.2)
  finché non riceve Ctrl+C o raggiunge MAX_CLIENTS.

Almeno un caso di errore gestito:
  Comando sconosciuto → ERROR unknown command
  Argomenti mancanti / in eccesso → ERROR bad syntax
  GET su chiave inesistente → NONE (non è un errore, è un risultato valido)
==============================================================================
"""

import socket
import threading

HOST        = "127.0.0.1"
PORT        = 65434          # porta dedicata per non collidere con gli altri esempi
MAX_CLIENTS = 10
BACKLOG     = 5


# ── Logica del key-value store ────────────────────────────────────────────────

def process_command(store: dict, raw: str) -> str:
    """
    Interpreta un comando testuale e restituisce la risposta da inviare.

    store : dizionario condiviso (per sessione, non tra client diversi)
    raw   : stringa ricevuta dal client (già stripped)

    Restituisce sempre una stringa; non lancia mai eccezioni.
    """
    parts = raw.split()
    if not parts:
        return "ERROR empty command"

    cmd = parts[0].upper()

    if cmd == "SET":
        if len(parts) < 3:
            return "ERROR bad syntax: SET <key> <value>"
        key   = parts[1]
        value = " ".join(parts[2:])  # value può contenere spazi
        store[key] = value
        return "OK"

    if cmd == "GET":
        if len(parts) != 2:
            return "ERROR bad syntax: GET <key>"
        value = store.get(parts[1])
        return f"VALUE {value}" if value is not None else "NONE"

    if cmd == "DEL":
        if len(parts) != 2:
            return "ERROR bad syntax: DEL <key>"
        store.pop(parts[1], None)
        return "OK"

    if cmd == "KEYS":
        if len(parts) != 1:
            return "ERROR bad syntax: KEYS (no arguments)"
        keys = list(store.keys())
        return f"KEYS {' '.join(keys)}" if keys else "KEYS"

    if cmd == "QUIT":
        return "BYE"

    return f"ERROR unknown command: {parts[0]!r}"


# ── Rete ──────────────────────────────────────────────────────────────────────

def create_server_socket(host: str, port: int) -> socket.socket:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(BACKLOG)
    print(f"[KV-Server] Listening on {host}:{port}")
    return server_sock


def handle_client(conn: socket.socket, addr: tuple) -> None:
    """
    Gestisce la sessione con un singolo client.
    Ogni client ha il proprio store privato: il dizionario non è condiviso
    tra connessioni diverse (semplificazione didattica; in un sistema reale
    lo store sarebbe condiviso e protetto da lock).
    """
    print(f"[KV-Server] [{addr}] Connected.")
    store = {}   # store privato per questa sessione

    try:
        # Ricezione di dati: un singolo recv() potrebbe non contenere un
        # comando completo se il payload è grande. Per messaggi brevi (< 1024 B)
        # è accettabile in un contesto didattico.
        while True:
            data = conn.recv(1024)
            if not data:
                print(f"[KV-Server] [{addr}] Disconnected (no data).")
                break

            raw = data.decode("utf-8").strip()
            print(f"[KV-Server] [{addr}] CMD: {raw!r}")

            response = process_command(store, raw)
            conn.sendall((response + "\n").encode("utf-8"))
            print(f"[KV-Server] [{addr}] RSP: {response!r}")

            if response == "BYE":
                break   # client ha inviato QUIT, chiudiamo lato server
    finally:
        conn.close()
        print(f"[KV-Server] [{addr}] Connection closed.")


def accept_loop(server_sock: socket.socket) -> None:
    client_count = 0
    while client_count < MAX_CLIENTS:
        print(f"\n[KV-Server] Waiting for connection ({client_count + 1}/{MAX_CLIENTS}) ...")
        conn, addr = server_sock.accept()
        client_count += 1
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()

    print(f"[KV-Server] Reached MAX_CLIENTS ({MAX_CLIENTS}). Shutting down.")


def main() -> None:
    server_sock = create_server_socket(HOST, PORT)
    try:
        accept_loop(server_sock)
    except KeyboardInterrupt:
        print("\n[KV-Server] Interrupted.")
    finally:
        server_sock.close()


if __name__ == "__main__":
    main()
