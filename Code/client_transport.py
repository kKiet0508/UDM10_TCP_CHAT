"""
Ket noi toi server va gui tin nhan tu ban phim.
"""
import socket
import sys

from config import SERVER_HOST, SERVER_PORT
from client_display import HELP_TEXT


def connect_client_socket():
    """Tao socket TCP va ket noi toi server."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        return client_socket
    except Exception as e:
        print(f"Khong the ket noi toi server: {e}")
        sys.exit(1)


def send_message(sock):
    """Doc tin nhan tu ban phim va gui len server."""
    while True:
        try:
            msg = input()
            if msg.strip().lower() in ("/help", "help"):
                print(HELP_TEXT)
                continue
            if msg.strip().lower() == "/leave":
                try:
                    sock.sendall(msg.encode("utf-8"))
                finally:
                    sock.close()
                return
            sock.sendall(msg.encode("utf-8"))
        except (ConnectionResetError, OSError, BrokenPipeError):
            break
    try:
        sock.close()
    except Exception:
        pass