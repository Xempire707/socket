"""
UDP Server — Ping Pong (educational example)

Author  : Pietro Boccadoro
Email   : pieroboccadoro13[at]gmail[dot]com
Date    : 2024-04-11
Version : 2.0  (Exercise 0 — refactored)

Key differences from TCP:
  - SOCK_DGRAM instead of SOCK_STREAM  →  UDP, connectionless
  - No listen() or accept()           →  no connection is ever "established"
  - recvfrom() instead of recv()      →  returns the sender's address with each datagram
  - sendto()   instead of sendall()   →  we must specify the destination every time
  - No close() on a per-client basis  →  there is no per-client socket to close
"""

import socket

HOST = "127.0.0.1"  # loopback — accetta datagrammi solo da questa macchina
PORT = 65433        # porta diversa da TCP per evitare conflitti


# ── Helpers ───────────────────────────────────────────────────────────────────

def create_udp_socket(host: str, port: int) -> socket.socket:
    """
    [MODIFICA] Nuova funzione.
    Crea e lega la socket UDP.
    Per UDP non servono listen() né accept(), quindi il setup è più corto
    rispetto al TCP, ma vale comunque la pena isolarlo per le stesse ragioni
    (leggibilità, facilità di modifica futura).
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"[Server] Listening for UDP datagrams on {host}:{port} ...")
    print("[Server] Press Ctrl+C to stop.\n")
    return sock


def build_reply(message: str) -> str:
    """
    [MODIFICA] Nuova funzione, identica alla versione TCP.
    Separare la logica applicativa dal codice di rete è importante
    soprattutto nell'Exercise 3 (packet loss): potremo decidere se
    droppare il pacchetto *dopo* aver già calcolato la risposta,
    senza mescolare le due responsabilità.
    """
    if message == "PING":
        return "PONG"
    return f"Unknown: {message!r}"


def receive_and_reply(sock: socket.socket) -> None:
    """
    [MODIFICA] Nuova funzione.
    Riceve un singolo datagramma, calcola la risposta e la invia.
    Separare "un ciclo di ricezione+risposta" in una funzione distinta
    rende il loop principale in serve_forever() banalmente leggibile
    e facilita l'aggiunta di logica extra (es. contatore per Exercise 1,
    drop simulato per Exercise 3) senza toccare il loop stesso.
    """
    data, client_addr = sock.recvfrom(1024)
    message = data.decode("utf-8").strip()
    print(f"[Server] Received {message!r} from {client_addr}")

    reply = build_reply(message)
    sock.sendto(reply.encode("utf-8"), client_addr)
    print(f"[Server] Sent {reply!r} back to {client_addr}\n")


def serve_forever(sock: socket.socket) -> None:
    """
    [MODIFICA] Nuova funzione.
    Loop infinito che chiama receive_and_reply() ad ogni iterazione.
    Isolare il loop permette di testarlo (es. mock della socket) e di
    sostituirlo facilmente con una variante asincrona in futuro.
    """
    while True:
        receive_and_reply(sock)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    """
    [MODIFICA] main() = setup + serve + (gestione Ctrl+C).
    Il KeyboardInterrupt era già nel codice originale, ma era nel blocco
    if __name__ == "__main__". Spostarlo dentro main() è più corretto:
    la logica di terminazione appartiene alla funzione che esegue il programma,
    non al punto di ingresso del modulo.
    """
    sock = create_udp_socket(HOST, PORT)
    try:
        serve_forever(sock)
    except KeyboardInterrupt:
        print("\n[Server] Stopped.")
    finally:
        # [MODIFICA] uso di finally per chiudere la socket anche in caso
        # di eccezioni impreviste (coerenza con il server TCP).
        sock.close()


if __name__ == "__main__":
    main()
