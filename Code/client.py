# -*- coding: utf-8 -*-
"""
Client - UDM_10 Chat Console via TCP
2 luồng: gửi message từ bàn phím, nhận message từ server
Hỗ trợ: /leave, /color, /private
"""

import socket
import threading
import sys

from colorama import Fore, Style, init

from config import SERVER_PORT, SERVER_HOST, BUFFER_SIZE

init(autoreset=True)

# Kết nối server (sửa SERVER_HOST trong config.py nếu server chạy máy khác)
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
except Exception as e:
    print(f"Cannot connect to server: {e}")
    sys.exit(1)

COLORS = {
    "red": Fore.RED,
    "green": Fore.GREEN,
    "yellow": Fore.YELLOW,
    "blue": Fore.BLUE,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "white": Fore.WHITE,
}


def print_message(message):
    """In message, hỗ trợ format /color: username: /color <mau> <nội dung>"""
    parts = message.split()
    if len(parts) >= 4 and parts[1] == "/color" and parts[2].lower() in COLORS:
        color = COLORS[parts[2].lower()]
        content = parts[0] + " " + " ".join(parts[3:])
        print(color + content + Style.RESET_ALL)
    else:
        print(message)


def receive_message():
    """Luồng nhận message từ server"""
    while True:
        try:
            data = client_socket.recv(BUFFER_SIZE).decode()
            if not data:
                break
            print_message(data)
        except (ConnectionResetError, OSError):
            break
        except Exception:
            break
    try:
        client_socket.close()
    except Exception:
        pass


def send_message():
    """Luồng gửi message từ bàn phím lên server"""
    while True:
        try:
            msg = input()
            # Gửi trước, sau đó mới đóng (để server nhận được /leave)
            if msg.strip().lower() == "/leave":
                client_socket.send(msg.encode())
                client_socket.close()
                return
            client_socket.send(msg.encode())
        except (ConnectionResetError, OSError, BrokenPipeError):
            break
        except Exception:
            break
    try:
        client_socket.close()
    except Exception:
        pass


# Chạy 2 luồng
recv_thread = threading.Thread(target=receive_message, daemon=True)
send_thread = threading.Thread(target=send_message, daemon=True)
recv_thread.start()
send_thread.start()
recv_thread.join()
send_thread.join()
