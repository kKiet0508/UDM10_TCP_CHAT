# -*- coding: utf-8 -*-
"""
Ket noi toi server va gui tin nhan tu ban phim.
"""
import socket
import sys

from config import SERVER_HOST, SERVER_PORT
from client_display import HELP_TEXT
from validation import normalize_username, validate_username


def send_message(sock, login_state):
    """
    login_state: dict co khoa 'need_username' = True cho toi khi da gui ten hop le.
    """
    while True:
        try:
            msg = input()
            stripped = msg.strip()
            lower = stripped.lower()

            if login_state.get("need_username"):
                name = normalize_username(msg)
                ok, err = validate_username(name)
                if not ok:
                    print(err)
                    print("Nhap lai ten dang nhap:")
                    continue
                try:
                    sock.sendall((name + "\n").encode("utf-8"))
                except (ConnectionResetError, OSError, BrokenPipeError):
                    return
                login_state["need_username"] = False
                continue

            if lower in ("/help", "help", "/?", "/"):
                print(HELP_TEXT)
                continue

            if lower == "/leave":
                try:
                    sock.sendall(msg.encode("utf-8"))
                finally:
                    sock.close()
                return

            sock.sendall(msg.encode("utf-8"))
        except (ConnectionResetError, OSError, BrokenPipeError):
            break
        except Exception:
            break
    try:
        sock.close()
    except Exception:
        pass


def connect_client_socket():
    """Tao socket TCP va ket noi toi server."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        return client_socket
    except Exception as e:
        print(f"Khong the ket noi toi server: {e}")
        sys.exit(1)
