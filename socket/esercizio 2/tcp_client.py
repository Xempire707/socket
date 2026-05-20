import socket
import time

HOST        = "127.0.0.1"  # address of the server (same machine)
PORT        = 65432         # must match tcp_server.py
NUM_PINGS   = 5             # [MODIFICA] costante estratta: prima era il valore letterale 6
                            # nell'argomento di range(). Centralizzare i "magic number"
                            # rende più semplice modificarli in un unico posto.
SLEEP_S     = 0.5           # [MODIFICA] pausa tra i ping estratta come costante


# ── Helpers ──────────────────────────────────────────────────────────────────

def create_connection(host: str, port: int) -> socket.socket:
    """
    [MODIFICA] Nuova funzione.
    Crea la socket TCP e stabilisce la connessione al server.
    Isolare questa operazione in una funzione ha due vantaggi:
      1. main() descrive *cosa* fa il programma, non *come* funziona la socket.
      2. In futuro (es. aggiungere TLS o un retry) si modifica solo qui.
    """
    # AF_INET = IPv4 | SOCK_STREAM = TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"[Client] Connected to {host}:{port}")
    return sock


def send_ping(sock: socket.socket, index: int) -> str:
    """
    [MODIFICA] Nuova funzione.
    Invia un singolo "PING" e restituisce la risposta decodificata come stringa.
    Separare l'I/O di rete dalla logica del loop rende il corpo del loop
    leggibile in una sola riga e permette di testare questa funzione in isolamento.

    Parametri
    ---------
    sock  : socket già connessa
    index : numero del ping corrente (usato solo per il log)
    """
    message = "PING"
    print(f"\n[Client] Send #{index}: {message!r}")

    # encode() → bytes; sendall() garantisce che tutti i byte vengano inviati
    sock.sendall(message.encode("utf-8"))

    # recv() blocca finché non arrivano dati (max 1024 byte)
    data = sock.recv(1024)
    return data.decode("utf-8")


def close_connection(sock: socket.socket) -> None:
    """
    [MODIFICA] Nuova funzione.
    Chiude la socket con un messaggio di log.
    Centralizzare il teardown evita di duplicarlo in più punti
    (es. nel ramo normale e in un eventuale except).
    """
    print("\n[Client] All pings sent. Closing connection.")
    sock.close()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    """
    [MODIFICA] main() è ora una sequenza di chiamate ad alto livello:
      1. apri connessione
      2. loop ping/pong
      3. chiudi connessione
    Tutta la logica di basso livello (socket, encode/decode) è nei moduli sopra.
    """
    sock = create_connection(HOST, PORT)

    for i in range(1, NUM_PINGS + 1):
        reply = send_ping(sock, i)
        print(f"[Client] Reply:    {reply!r}")
        time.sleep(SLEEP_S)

    close_connection(sock)


if __name__ == "__main__":
    main()
