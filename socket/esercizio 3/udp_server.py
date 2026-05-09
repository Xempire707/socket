"""
UDP Server — Canale inaffidabile simulato (Exercise 3)

Author  : Pietro Boccadoro
Email   : pieroboccadoro13[at]gmail[dot]com
Date    : 2024-04-11
Version : 3.0  (Exercise 3 — unreliable channel simulation)

Novità rispetto a Exercise 0:
  - DROP_PROBABILITY: costante tra 0.0 e 1.0. Con 0.3 il 30% dei PONG
    viene "perso" (non inviato).
  - Prima di inviare ogni risposta, random.random() estrae un numero
    casuale; se è < DROP_PROBABILITY il sendto() viene saltato e viene
    stampato un messaggio di log.
  - Questo rende essenziale il timeout nel client (già presente da Ex.0):
    senza timeout, recvfrom() bloccherebbe per sempre sui pacchetti droppati.

Osservazione didattica:
  Su localhost i pacchetti non si perdono mai davvero. Questo drop
  simulato lato server permette di osservare il comportamento del client
  (timeout, stampa del messaggio, continuazione) senza infrastruttura reale.
"""

import socket
import random

HOST             = "127.0.0.1"
PORT             = 65433
DROP_PROBABILITY = 0.3   # 30% di probabilità di non inviare la risposta


def create_udp_socket(host: str, port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"[Server] Listening on {host}:{port}  "
          f"(drop probability: {DROP_PROBABILITY:.0%})")
    print("[Server] Press Ctrl+C to stop.\n")
    return sock


def build_reply(message: str) -> str:
    if message == "PING":
        return "PONG"
    return f"Unknown: {message!r}"


def should_drop() -> bool:
    """
    [NUOVO rispetto a Ex.0] Restituisce True se questo pacchetto va droppato.
    Separare la decisione di drop in una funzione la rende facile da testare
    (sostituire random.random con un mock) e facile da leggere in
    receive_and_reply().
    """
    return random.random() < DROP_PROBABILITY


def receive_and_reply(sock: socket.socket) -> None:
    """
    Rispetto a Ex.0: dopo aver calcolato la risposta, controlla should_drop().
    Se il pacchetto va droppato, stampa il messaggio di log e NON chiama
    sendto(). Il client riceverà un timeout su questo ping.
    """
    data, client_addr = sock.recvfrom(1024)
    message = data.decode("utf-8").strip()
    print(f"[Server] Received {message!r} from {client_addr}")

    reply = build_reply(message)

    if should_drop():
        # Simula perdita del pacchetto: non inviamo nulla
        print(f"[Server] Dropped reply (simulated loss) → client vedrà timeout\n")
        return

    sock.sendto(reply.encode("utf-8"), client_addr)
    print(f"[Server] Sent {reply!r} to {client_addr}\n")


def serve_forever(sock: socket.socket) -> None:
    while True:
        receive_and_reply(sock)


def main() -> None:
    sock = create_udp_socket(HOST, PORT)
    try:
        serve_forever(sock)
    except KeyboardInterrupt:
        print("\n[Server] Stopped.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
