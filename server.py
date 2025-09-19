import socket
import threading

HOST = "127.0.0.1"
PORT = 5000

clients = set()           # set de sockets
names = {}                # conn -> nome
lock = threading.Lock()

def broadcast(msg: str, sender=None):
    data = (msg + "\n").encode("utf-8")
    dead = []
    with lock:
        for c in list(clients):
            if c is sender:
                continue
            try:
                c.sendall(data)
            except Exception:
                dead.append(c)
        # limpar conexões mortas
        for c in dead:
            clients.discard(c)
            n = names.pop(c, None)
            try: c.close()
            except: pass

def handle_client(conn: socket.socket, addr):
    try:
        # usar "arquivo" para ler por linhas (evita mensagens cortadas no meio)
        f = conn.makefile("r", encoding="utf-8", newline="\n")

        conn.sendall(b"Digite seu nome: ")
        name = f.readline()
        if not name:
            return
        name = name.strip() or f"{addr[0]}:{addr[1]}"

        with lock:
            clients.add(conn)
            names[conn] = name

        broadcast(f"🟢 {name} entrou no chat.")

        for line in f:
            msg = line.rstrip("\n")
            if msg == "/sair":
                conn.sendall("Você saiu do chat. Até mais!\n".encode("utf-8"))
                break
            if msg:  # ignora linhas vazias
                broadcast(f"{name}: {msg}", sender=conn)

    except Exception:
        pass
    finally:
        with lock:
            if conn in clients:
                clients.remove(conn)
            leaving = names.pop(conn, None)
        try:
            conn.close()
        except:
            pass
        if leaving:
            broadcast(f"🔴 {leaving} saiu do chat.")

def main():
    print(f"Servidor ouvindo em {HOST}:{PORT} ...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
