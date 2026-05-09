"""
UDP Server — Ping Pong con contatore messaggi (Exercise 1)

Author  : Pietro Boccadoro
Email   : pieroboccadoro13[at]gmail[dot]com
Date    : 2024-04-11
Version : 3.0  (Exercise 1 — message counter)

Novità rispetto a Exercise 0:
  - Il server mantiene un contatore globale dei PING ricevuti.
  - Ogni risposta PONG include il contatore: es. "PONG #3".
  - Il contatore è una variabile locale di serve_forever() inizializzata a 0:
    scelta deliberata perché il suo scope è esattamente il ciclo di vita
    del server. Se il server viene riavviato il contatore riparte da 0
    (comportamento desiderabile: un nuovo processo è una nuova sessione).
    Se il client si riconnette senza riavviare il server, il contatore
    continua a salire — il client vedrà numeri non ricominciati da 1.

Dove vive il contatore?
  - È un intero locale in serve_forever(). Non è necessario renderlo
    globale o un attributo di classe perché serve_forever() è l'unica
    funzione che lo legge e lo modifica.
  - Viene passato a receive_and_reply() che restituisce il contatore
    aggiornato: approccio funzionale che evita side-effect nascosti.
"""

import socket

HOST = "127.0.0.1"
PORT = 65433


def create_udp_socket(host: str, port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"[Server] Listening for UDP datagrams on {host}:{port} ...")
    print("[Server] Press Ctrl+C to stop.\n")
    return sock


def build_reply(message: str, ping_count: int) -> str:
    """
    Rispetto a Ex.0: accetta ping_count e lo include nella risposta PONG.
    La logica di formattazione resta centralizzata qui.
    """
    if message == "PING":
        return f"PONG #{ping_count}"   # es. "PONG #3"
    return f"Unknown: {message!r}"


def receive_and_reply(sock: socket.socket, ping_count: int) -> int:
    """
    Rispetto a Ex.0: riceve ping_count, lo incrementa se il messaggio è PING,
    e restituisce il nuovo valore. Pattern funzionale: nessuno stato globale mutato.
    """
    data, client_addr = sock.recvfrom(1024)
    message = data.decode("utf-8").strip()
    print(f"[Server] Received {message!r} from {client_addr}")

    if message == "PING":
        ping_count += 1  # incrementa solo sui PING validi

    reply = build_reply(message, ping_count)
    sock.sendto(reply.encode("utf-8"), client_addr)
    print(f"[Server] Sent {reply!r} to {client_addr}  (total PINGs: {ping_count})\n")

    return ping_count


def serve_forever(sock: socket.socket) -> None:
    """
    Rispetto a Ex.0: ping_count nasce qui a zero e viene aggiornato
    ad ogni iterazione con il valore restituito da receive_and_reply().
    """
    ping_count = 0
    while True:
        ping_count = receive_and_reply(sock, ping_count)


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
