"""
UDP Client — Ping Pong con contatore visibile (Exercise 1)

Author  : Pietro Boccadoro
Email   : pieroboccadoro13[at]gmail[dot]com
Date    : 2024-04-11
Version : 3.0  (Exercise 1 — message counter)

Modifica rispetto a Exercise 0:
  - Il client stampa la risposta completa del server (es. "PONG #3")
    invece di assumerla sempre uguale a "PONG".
  - Nessuna modifica alla logica di rete: il cambiamento è puramente
    nel layer di presentazione (il print in send_ping).
"""

import socket
import time

HOST        = "127.0.0.1"
PORT        = 65433
BUFFER_SIZE = 1024
NUM_PINGS   = 5
TIMEOUT_S   = 2.0
SLEEP_S     = 0.5


def create_udp_socket(timeout: float) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    print(f"[Client] UDP socket ready. Will send to {HOST}:{PORT}\n")
    return sock


def send_ping(sock: socket.socket, host: str, port: int, index: int) -> None:
    """
    Rispetto a Ex.0: il print mostra reply (es. "PONG #3") invece del
    testo fisso "PONG", in modo da rendere il contatore del server visibile
    lato client.
    """
    message = "PING"
    print(f"[Client] Send #{index}: {message!r}")
    sock.sendto(message.encode("utf-8"), (host, port))

    try:
        data, server_addr = sock.recvfrom(BUFFER_SIZE)
        reply = data.decode("utf-8")
        # Stampa la risposta completa: "PONG #1", "PONG #2", ecc.
        print(f"[Client] Reply from {server_addr}: {reply!r}")
    except socket.timeout:
        print(f"[Client] Timeout — no reply received for ping #{index}")


def close_socket(sock: socket.socket) -> None:
    print("\n[Client] Done. Closing socket.")
    sock.close()


def main() -> None:
    sock = create_udp_socket(TIMEOUT_S)
    for i in range(1, NUM_PINGS + 1):
        send_ping(sock, HOST, PORT, i)
        time.sleep(SLEEP_S)
    close_socket(sock)


if __name__ == "__main__":
    main()
