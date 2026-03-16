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

init(autoreset=True, convert=True)  # convert=True cần cho Windows

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
    """In message. Format: [Client] user: ... hoac [Server] ... Hỗ trợ /color."""
    parts = message.split()
    # Tìm /color trong message (vd: [Client] Phat: /color red hello)
    for i, p in enumerate(parts):
        if p == "/color" and i + 1 < len(parts):
            color_name = parts[i + 1].strip("<>").lower()
            if color_name in COLORS:
                content = " ".join(parts[:i] + parts[i + 2:])
                print(COLORS[color_name] + content + Style.RESET_ALL, flush=True)
                return
            break
    print(message)


def receive_message(sock):
    """Luồng nhận message từ server (phân tách theo \\n)"""
    buffer = ""
    while True:
        try:
            data = sock.recv(BUFFER_SIZE).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)
                msg = msg.strip()
                if msg:
                    print_message(msg)
        except (ConnectionResetError, OSError):
            break
        except Exception:
            break
    try:
        sock.close()
    except Exception:
        pass


HELP_TEXT = """
--- LENH CHAT (go dung nhu vi du, KHONG dung dau < >) ---
/list                    Xem user online
/private kiet xin chao    Tin nhan rieng (vd: /private thuong hello)
/color red hello          Tin nhan mau (mau: red,green,yellow,blue,magenta,cyan,white)
/leave                    Thoat chat
/help                     Xem lai huong dan
"""


def send_message(sock):
    """Luồng gửi message từ bàn phím lên server"""
    while True:
        try:
            msg = input()
            stripped = msg.strip()
            lower = stripped.lower()
            # Gợi ý khi gõ / sai
            if lower in ("/", "/?", "help"):
                print(HELP_TEXT)
                continue
            if lower == "/help":
                print(HELP_TEXT)
                continue
            # Gửi trước, sau đó mới đóng (để server nhận được /leave)
            if lower == "/leave":
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
