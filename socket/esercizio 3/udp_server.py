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
