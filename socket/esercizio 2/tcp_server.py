import socket
import threading

HOST        = "127.0.0.1"
PORT        = 65432
MAX_CLIENTS = 3      # il server si ferma dopo aver servito questo numero di client
THREADED    = True   # True = un thread per client; False = sequenziale


def create_server_socket(host: str, port: int) -> socket.socket:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(5)   # backlog aumentato a 5 per la modalità threaded
    print(f"[Server] Listening on {host}:{port}  "
          f"(max_clients={MAX_CLIENTS}, threaded={THREADED})")
    return server_sock


def build_reply(message: str) -> str:
    if message == "PING":
        return "PONG"
    return f"Unknown message: {message!r}"


def handle_client(conn: socket.socket, addr: tuple) -> None:
    """
    Gestisce la sessione con un singolo client.
    Identica a Ex.0, ma ora può essere eseguita sia nel thread principale
    (sequenziale) sia in un thread dedicato (THREADED=True).
    addr viene passato per il log, in modo che in modalità threaded
    sia sempre chiaro quale client sta rispondendo.
    """
    print(f"[Server] [{addr}] Connection accepted.")
    while True:
        data = conn.recv(1024)
        if not data:
            print(f"[Server] [{addr}] Client disconnected.")
            break
        message = data.decode("utf-8").strip()
        print(f"[Server] [{addr}] Received: {message!r}")
        reply = build_reply(message)
        conn.sendall(reply.encode("utf-8"))
        print(f"[Server] [{addr}] Sent:     {reply!r}")
    conn.close()


def accept_loop(server_sock: socket.socket) -> None:
    """
    [NUOVO rispetto a Ex.0] Loop che accetta fino a MAX_CLIENTS connessioni.

    Modalità sequenziale (THREADED=False):
      handle_client() viene chiamata direttamente → il server blocca
      finché il client corrente non chiude la connessione, poi accetta
      il prossimo.

    Modalità threaded (THREADED=True):
      handle_client() viene passata come target di un Thread → il thread
      principale torna subito ad accept() permettendo connessioni simultanee.
      daemon=True garantisce che i thread figli non blocchino l'uscita
      del processo principale.
    """
    for client_num in range(1, MAX_CLIENTS + 1):
        print(f"\n[Server] Waiting for client {client_num}/{MAX_CLIENTS} ...")
        conn, addr = server_sock.accept()

        if THREADED:
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
            print(f"[Server] Spawned thread {t.name} for {addr}")
        else:
            handle_client(conn, addr)

    print(f"\n[Server] Reached MAX_CLIENTS ({MAX_CLIENTS}). Shutting down.")


def main() -> None:
    server_sock = create_server_socket(HOST, PORT)
    try:
        accept_loop(server_sock)
    except KeyboardInterrupt:
        print("\n[Server] Interrupted.")
    finally:
        server_sock.close()


if __name__ == "__main__":
    main()
