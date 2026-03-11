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


def receive_message(sock):
    """Luồng nhận message từ server"""
    while True:
        try:
            data = sock.recv(BUFFER_SIZE).decode()
            if not data:
                break
            print_message(data)
        except (ConnectionResetError, OSError):
            break
        except Exception:
            break
    try:
        sock.close()
    except Exception:
        pass


def send_message(sock):
    """Luồng gửi message từ bàn phím lên server"""
    while True:
        try:
            msg = input()
            # Gửi trước, sau đó mới đóng (để server nhận được /leave)
            if msg.strip().lower() == "/leave":
                sock.send(msg.encode())
                sock.close()
                return
            sock.send(msg.encode())
        except (ConnectionResetError, OSError, BrokenPipeError):
            break
        except Exception:
            break
    try:
        sock.close()
    except Exception:
        pass


def main():
    """Kết nối server và chạy chat"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
    except Exception as e:
        print(f"Cannot connect to server: {e}")
        sys.exit(1)

    recv_thread = threading.Thread(target=receive_message, args=(client_socket,), daemon=True)
    send_thread = threading.Thread(target=send_message, args=(client_socket,), daemon=True)
    recv_thread.start()
    send_thread.start()
    recv_thread.join()
    send_thread.join()


if __name__ == "__main__":
    main()
