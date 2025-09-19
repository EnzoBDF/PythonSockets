import socket
import threading
import sys
import os

HOST = "127.0.0.1"
PORT = 5000

def receiver(conn: socket.socket):
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                print("\n[Conexão encerrada pelo servidor]")
                break
            print(data.decode("utf-8"), end="")
    except Exception:
        pass
    finally:
        try: conn.close()
        except: pass
        os._exit(0)  # encerra o processo para não deixar stdin travado

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
        try:
            conn.connect((HOST, PORT))
        except Exception as e:
            print(f"Não foi possível conectar: {e}")
            return

        # prompt de nome
        first = conn.recv(1024).decode("utf-8")
        print(first, end="")
        name = input().strip()
        conn.sendall((name + "\n").encode("utf-8"))

        print("Conectado! Digite mensagens e pressione Enter.")
        print("Para sair, digite /sair e pressione Enter.")

        t = threading.Thread(target=receiver, args=(conn,), daemon=True)
        t.start()

        try:
            for line in sys.stdin:
                msg = line.rstrip("\r\n")
                conn.sendall((msg + "\n").encode("utf-8"))
                if msg == "/sair":
                    break
        except KeyboardInterrupt:
            try: conn.sendall(b"/sair\n")
            except: pass
        finally:
            try: conn.shutdown(socket.SHUT_RDWR)
            except: pass
            conn.close()

if __name__ == "__main__":
    main()

