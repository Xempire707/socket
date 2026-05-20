import socket

HOST = "127.0.0.1"
PORT = 65434


def create_connection(host: str, port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"[KV-Client] Connected to {host}:{port}")
    print("[KV-Client] Commands: SET <key> <value> | GET <key> | DEL <key> | KEYS | QUIT\n")
    return sock


def send_command(sock: socket.socket, command: str) -> str:
    """
    Invia un comando al server e restituisce la risposta.
    La risposta termina con '\\n' (aggiunta dal server); strip() la rimuove.
    """
    sock.sendall((command + "\n").encode("utf-8"))
    data = sock.recv(1024)
    return data.decode("utf-8").strip()


def interactive_loop(sock: socket.socket) -> None:
    """
    Loop interattivo: legge un comando da stdin, lo invia al server,
    stampa la risposta. Termina quando:
      - l'utente digita QUIT (server risponde BYE)
      - l'utente preme Ctrl+C
      - la connessione viene chiusa dall'esterno
    """
    while True:
        try:
            command = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[KV-Client] Interrupted.")
            break

        if not command:
            continue  # riga vuota → ricicla

        response = send_command(sock, command)
        print(f"    {response}")

        if response == "BYE":
            break  # server ha confermato QUIT, usciamo


def close_connection(sock: socket.socket) -> None:
    print("[KV-Client] Closing connection.")
    sock.close()


def main() -> None:
    sock = create_connection(HOST, PORT)
    try:
        interactive_loop(sock)
    finally:
        close_connection(sock)


if __name__ == "__main__":
    main()
