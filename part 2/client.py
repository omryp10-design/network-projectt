import socket
import threading

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5555

def recv_loop(sock: socket.socket):
    try:
        f = sock.makefile("r", encoding="utf-8", newline="\n")
        while True:
            line = f.readline()
            if not line:
                print("[Disconnected]")
                break
            print(line.rstrip("\n"))
    except Exception:
        print("[Disconnected]")
    finally:
        try:
            sock.close()
        except OSError:
            pass

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))
    print(f"Connected to {SERVER_IP}:{SERVER_PORT}. Type messages, /quit to exit.")

    threading.Thread(target=recv_loop, args=(sock,), daemon=True).start()

    while True:
        msg = input()
        try:
            sock.sendall((msg + "\n").encode("utf-8", errors="replace"))
        except OSError:
            print("[Send failed]")
            break
        if msg == "/quit":
            break

    try:
        sock.close()
    except OSError:
        pass

if __name__ == "__main__":
    main()
