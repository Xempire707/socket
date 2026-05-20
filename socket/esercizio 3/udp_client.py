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


def send_ping(sock: socket.socket, host: str, port: int, index: int) -> bool:
    """
    Rispetto a Ex.0: restituisce True se la risposta è arrivata, False se
    è scaduto il timeout. Il valore di ritorno permette al chiamante di
    tenere le statistiche senza accedere a stato interno.
    Il messaggio di timeout è più descrittivo rispetto a Ex.0.
    """
    message = "PING"
    print(f"[Client] Send #{index}: {message!r}")
    sock.sendto(message.encode("utf-8"), (host, port))

    try:
        data, server_addr = sock.recvfrom(BUFFER_SIZE)
        reply = data.decode("utf-8")
        print(f"[Client] Reply from {server_addr}: {reply!r}")
        return True
    except socket.timeout:
        # Messaggio esplicito: il client sa che potrebbe essere una perdita simulata
        print(f"[Client] Ping #{index} lost (server simulated drop or unreachable)")
        return False


def print_summary(received: int, total: int) -> None:
    """
    [NUOVO rispetto a Ex.0] Stampa le statistiche finali della sessione.
    Utile per osservare l'effetto di DROP_PROBABILITY in modo quantitativo.
    """
    lost = total - received
    print(f"\n[Client] Summary: {received}/{total} received, {lost}/{total} lost")


def close_socket(sock: socket.socket) -> None:
    print("[Client] Closing socket.")
    sock.close()


def main() -> None:
    sock = create_udp_socket(TIMEOUT_S)
    received = 0

    for i in range(1, NUM_PINGS + 1):
        if send_ping(sock, HOST, PORT, i):
            received += 1
        time.sleep(SLEEP_S)

    print_summary(received, NUM_PINGS)
    close_socket(sock)


if __name__ == "__main__":
    main()
