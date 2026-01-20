import socket
import threading

HOST = "0.0.0.0"
PORT = 5555

clients = {}  # nickname -> socket
lock = threading.Lock()

def safe_send(sock: socket.socket, text: str) -> bool:
    try:
        sock.sendall((text + "\n").encode("utf-8", errors="replace"))
        return True
    except OSError:
        return False

def broadcast(text: str, exclude_sock: socket.socket | None = None):
    with lock:
        items = list(clients.items())

    dead = []
    for nickname, sock in items:
        if sock is exclude_sock:
            continue
        ok = safe_send(sock, text)
        if not ok:
            dead.append(nickname)

    if dead:
        with lock:
            for n in dead:
                s = clients.pop(n, None)
                try:
                    if s:
                        s.close()
                except OSError:
                    pass

def handle_client(conn: socket.socket, addr, nickname: str):
    print(f"[+] {nickname} connected from {addr}")

    with lock:
        clients[nickname] = conn

    safe_send(conn, f"Welcome {nickname}! Type messages, /quit to exit.")
    broadcast(f"* {nickname} joined *", exclude_sock=None)

    try:
        # line-based protocol: each message ends with \n
        f = conn.makefile("r", encoding="utf-8", newline="\n")

        while True:
            line = f.readline()
            if not line:  # disconnected
                break

            msg = line.rstrip("\n")
            if msg == "/quit":
                break

            print(f"{nickname}: {msg}")
            broadcast(f"{nickname}: {msg}", exclude_sock=conn)

    except Exception:
        pass
    finally:
        with lock:
            clients.pop(nickname, None)

        try:
            conn.close()
        except OSError:
            pass

        broadcast(f"* {nickname} left *", exclude_sock=None)
        print(f"[-] {nickname} disconnected")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(50)

    print(f"Server started on {HOST}:{PORT} ...")

    counter = 1
    while True:
        conn, addr = server.accept()
        nickname = f"Client {counter}"
        counter += 1
        threading.Thread(target=handle_client, args=(conn, addr, nickname), daemon=True).start()

if __name__ == "__main__":
    main()
