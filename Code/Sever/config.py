# -*- coding: utf-8 -*-
"""
Cau hinh chung + gioi han do dai / thong bao loi validation.
"""
import socket

# Network
SERVER_PORT = 1234
SERVER_HOST = "127.0.0.1"
BUFFER_SIZE = 1024

# Gioi han validation (username + tin nhan chat)
USERNAME_MIN_LEN = 3
USERNAME_MAX_LEN = 32
CHAT_LINE_MAX_LEN = 2000

# Admin (user có quyền /kick, /ban)
ADMIN_USERNAME = "admin"

# Messages
WELCOME_MESSAGE = "Welcome to the chatroom, to continue enter your username: "
REJECTED_MESSAGE = "Sorry, your request was denied. Try again later."
DUPLICATE_USERNAME_MESSAGE = "Username already exists. Please choose another."
BANNED_MESSAGE = "You are banned from this chatroom."
KICKED_MESSAGE = "You have been kicked from the chatroom."

# Validation (login username)
INVALID_USERNAME_EMPTY = "Ten dang nhap khong duoc de trong. Hay ket noi lai."
INVALID_USERNAME_SHORT = (
    f"Ten qua ngan (toi thieu {USERNAME_MIN_LEN} ky tu). Thu lai."
)
INVALID_USERNAME_LONG = (
    f"Ten qua dai (toi da {USERNAME_MAX_LEN} ky tu). Hay rut ngan va ket noi lai."
)
INVALID_USERNAME_CHARS = (
    "Ten chi duoc chua chu cai (co the co dau), so, _ hoac -. Khong dung ky tu la."
)
USERNAME_LINE_TOO_LONG = "Dong ten qua dai. Hay ket noi lai voi ten ngan hon."
LINE_TOO_LONG_MESSAGE = (
    f"Tin nhan qua dai (toi da {CHAT_LINE_MAX_LEN} ky tu). Hay gui ngan lai."
)

OPTIONS_MESSAGE = (
    "You are added to the chatroom. Messages you send are broadcast to other users.\n"
    "Commands (KHONG dung dau < >, go dung nhu vi du):\n"
    "  /list                          - Xem danh sach user dang online\n"
    "  /private username message      - Vi du: /private kiet xin chao\n"
    "  /color mau message             - Vi du: /color red hello\n"
    "  /leave                         - Thoat chat\n"
    "  /help                          - Xem lai huong dan\n"
)
ADMIN_OPTIONS = (
    "  /kick username         - Vi du: /kick thuong\n"
    "  /ban username          - Vi du: /ban kiet\n"
)


def get_server_address():
    """Lay dia chi IP theo hostname (khi can hien thi cho LAN)."""
    return socket.gethostbyname(socket.gethostname())
