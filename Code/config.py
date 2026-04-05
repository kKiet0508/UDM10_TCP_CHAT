# -*- coding: utf-8 -*-
"""
Người 1 — Cấu hình chung: port, host, buffer, admin, toàn bộ chuỗi hệ thống.
Cấu hình chung cho Server và Client - UDM_10 Chat Console via TCP
"""

import socket

# Network
SERVER_PORT = 1234
SERVER_HOST = "127.0.0.1"
BUFFER_SIZE = 1024

# Admin (user có quyền /kick, /ban)
ADMIN_USERNAME = "admin"

# Messages
WELCOME_MESSAGE = "Welcome to the chatroom, to continue enter your username: "
REJECTED_MESSAGE = "Sorry, your request was denied. Try again later."
DUPLICATE_USERNAME_MESSAGE = "Username already exists. Please choose another."
BANNED_MESSAGE = "You are banned from this chatroom."
KICKED_MESSAGE = "You have been kicked from the chatroom."

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
    """Lấy địa chỉ server (dùng gethostname nếu chạy cùng máy)"""
    return socket.gethostbyname(socket.gethostname())
