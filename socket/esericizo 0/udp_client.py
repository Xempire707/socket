import socket
import time

HOST        = "127.0.0.1"  # indirizzo del server
PORT        = 65433         # deve corrispondere a udp_server.py
BUFFER_SIZE = 1024          # dimensione massima del datagramma di risposta
NUM_PINGS   = 5             # [MODIFICA] estratto come costante (era literale nel range)
TIMEOUT_S   = 2.0           # [MODIFICA] estratto come costante (era literale in settimeout)
SLEEP_S     = 0.5           # [MODIFICA] estratto come costante (era literale in sleep)


# ── Helpers ───────────────────────────────────────────────────────────────────

def create_udp_socket(timeout: float) -> socket.socket:
    """
    [MODIFICA] Nuova funzione.
    Crea la socket UDP e imposta il timeout.
    Stessa motivazione del TCP: main() non deve occuparsi dei dettagli
    di costruzione/configurazione della socket.
    """
    # AF_INET = IPv4 | SOCK_DGRAM = UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    print(f"[Client] UDP socket ready. Will send to {HOST}:{PORT}\n")
    return sock


def send_ping(sock: socket.socket, host: str, port: int, index: int) -> None:
    """
    [MODIFICA] Nuova funzione.
    Invia un datagramma "PING" e stampa la risposta (o il messaggio di timeout).
    Raccogliere il try/except qui evita di annidarlo nel corpo del loop in main(),
    mantenendo main() piatto e leggibile.
    Il timeout è gestito internamente: il chiamante non deve preoccuparsene.
    """
    message = "PING"
    print(f"[Client] Send #{index}: {message!r}")

    # sendto() richiede l'indirizzo di destinazione ad ogni chiamata
    # (UDP è connectionless: non c'è una "connessione corrente" da usare)
    sock.sendto(message.encode("utf-8"), (host, port))

    try:
        data, server_addr = sock.recvfrom(BUFFER_SIZE)
        reply = data.decode("utf-8")
        print(f"[Client] Reply from {server_addr}: {reply!r}")
    except socket.timeout:
        # Il server non ha risposto entro TIMEOUT_S secondi.
        # Con UDP ciò può accadere per perdita del datagramma o server non disponibile.
        print(f"[Client] Timeout — no reply received for ping #{index}")


def close_socket(sock: socket.socket) -> None:
    """
    [MODIFICA] Nuova funzione per il teardown (coerenza con il client TCP).
    """
    print("\n[Client] Done. Closing socket.")
    sock.close()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    """
    [MODIFICA] main() ridotto a: crea socket → loop ping → chiudi.
    Ogni dettaglio è delegato alle funzioni sopra.
    """
    sock = create_udp_socket(TIMEOUT_S)

    for i in range(1, NUM_PINGS + 1):
        send_ping(sock, HOST, PORT, i)
        time.sleep(SLEEP_S)

    close_socket(sock)


if __name__ == "__main__":
    main()
