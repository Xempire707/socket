import socket

HOST = "127.0.0.1"  # loopback — accetta solo connessioni locali
PORT = 65432        # porta > 1024: non richiede privilegi root


# ── Helpers ───────────────────────────────────────────────────────────────────

def create_server_socket(host: str, port: int) -> socket.socket:
    """
    [MODIFICA] Nuova funzione.
    Crea, configura (SO_REUSEADDR), lega e mette in ascolto la socket server.
    Raggruppare questi 4 passi in una funzione chiarisce che si tratta di
    un'unica fase di "setup": il chiamante riceve una socket già pronta
    ad accettare connessioni, senza conoscerne i dettagli implementativi.
    """
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # SO_REUSEADDR evita "Address already in use" ai riavvii rapidi
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(1)
    print(f"[Server] Listening on {host}:{port} ...")
    return server_sock


def accept_client(server_sock: socket.socket) -> tuple[socket.socket, tuple]:
    """
    [MODIFICA] Nuova funzione (wrapper sottile su accept()).
    Blocca finché un client completa il three-way handshake,
    poi logga l'indirizzo e restituisce (conn, addr).
    Separare accept() dal loop di comunicazione rende entrambe le parti
    più leggibili e faciliterà l'Exercise 2 (multi-client).
    """
    conn, addr = server_sock.accept()
    print(f"[Server] Connection accepted from {addr}")
    return conn, addr


def build_reply(message: str) -> str:
    """
    [MODIFICA] Nuova funzione.
    Calcola la risposta da inviare dato il messaggio ricevuto.
    Isolare la logica applicativa (quale risposta dare) dal codice di rete
    (come inviare la risposta) rispetta il principio di singola responsabilità
    e rende più semplice aggiungere nuovi comandi in futuro senza toccare
    il loop di comunicazione.
    """
    if message == "PING":
        return "PONG"
    return f"Unknown message: {message!r}"


def handle_client(conn: socket.socket) -> None:
    """
    [MODIFICA] Nuova funzione.
    Gestisce l'intera sessione con un singolo client connesso:
    legge messaggi in loop finché il client chiude la connessione,
    poi chiude la socket lato server.
    Estrarre questo loop in una funzione separata è il prerequisito
    diretto per l'Exercise 2 (threading: basterà passare questa funzione
    come target di un Thread).
    """
    while True:
        data = conn.recv(1024)

        # recv() restituisce b"" quando il client chiude la connessione
        if not data:
            print("[Server] Client closed the connection.")
            break

        message = data.decode("utf-8").strip()
        print(f"[Server] Received: {message!r}")

        reply = build_reply(message)
        conn.sendall(reply.encode("utf-8"))
        print(f"[Server] Sent:     {reply!r}")

    conn.close()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    """
    [MODIFICA] main() è ora una sequenza ad alto livello:
      1. setup server socket
      2. accetta un client
      3. gestisce il client
      4. teardown
    La separazione in funzioni rende già evidente dove agire per l'Exercise 2
    (avvolgere i passi 2-3 in un loop / thread).
    """
    server_sock = create_server_socket(HOST, PORT)

    try:
        conn, _ = accept_client(server_sock)
        handle_client(conn)
    finally:
        # [MODIFICA] uso di try/finally per garantire la chiusura della
        # socket server anche in caso di eccezione imprevista.
        server_sock.close()


if __name__ == "__main__":
    main()
