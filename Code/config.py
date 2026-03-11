# -*- coding: utf-8 -*-
"""
Cấu hình chung cho Server và Client - UDM_10 Chat Console via TCP
"""

import socket

# Network
SERVER_PORT = 1234
SERVER_HOST = "127.0.0.1"  # localhost - đổi nếu chạy trên máy khác
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
    "Commands:\n"
    "  /list                    - List connected clients\n"
    "  /private <user> <msg>    - Send private message\n"
    "  /color <color> <msg>     - Send colored message (red, green, yellow, blue, magenta, cyan, white)\n"
    "  /leave                   - Leave the chatroom\n"
)
# Admin-only commands (thêm vào OPTIONS nếu user là admin)
ADMIN_OPTIONS = (
    "  /kick <username>         - Kick user (admin only)\n"
    "  /ban <username>          - Ban user (admin only)\n"
)


def get_server_address():
    """Lấy địa chỉ server (dùng gethostname nếu chạy cùng máy)"""
    return socket.gethostbyname(socket.gethostname())
