# -*- coding: utf-8 -*-
"""
Hien tin nhan tu server va khoi chay client
"""
from colorama import Fore, Style, init

from config import BUFFER_SIZE

init(autoreset=True, convert=True)

COLORS = {
    "red": Fore.RED,
    "green": Fore.GREEN,
    "yellow": Fore.YELLOW,
    "blue": Fore.BLUE,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "white": Fore.WHITE,
}

HELP_TEXT = """
--- LENH CHAT ---
/list                      Xem user online
/private <user> <message>  Gui tin nhan rieng (vd: /private kiet xin chao)
/color <mau> <message>     Gui tin co mau (vd: /color red hello)
/leave                     Thoat chat
/help                      Xem lai huong dan
"""


def print_message(message):
    """In tin nhan, co mau neu dung lenh /color."""
    parts = message.split()
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
    """Nhan du lieu tu socket va hien thi len man hinh."""
    buffer = ""
    while True:
        try:
            data = sock.recv(BUFFER_SIZE).decode("utf-8", errors="replace")
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
