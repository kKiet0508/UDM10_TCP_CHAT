# -*- coding: utf-8 -*-
"""
Server - UDM_10 Chat Console via TCP
Xử lý: login, broadcast, private message, /list, /kick, /ban, thông báo join/leave
"""

import socket
import threading

from config import (
    SERVER_PORT,
    ADMIN_USERNAME,
    BUFFER_SIZE,
    WELCOME_MESSAGE,
    REJECTED_MESSAGE,
    DUPLICATE_USERNAME_MESSAGE,
    BANNED_MESSAGE,
    KICKED_MESSAGE,
    OPTIONS_MESSAGE,
    ADMIN_OPTIONS,
)

# Lưu trữ: addr -> username, username -> addr, addr -> socket
addr_to_username = {}
username_to_addr = {}
connected_clients = {}
banned_users = set()

# Lock cho thread-safe khi sửa dict
lock = threading.Lock()


def is_user_allowed(connection_socket, user_name):
    """Admin approve/reject client muốn join (y/n)"""
    while True:
        cmd = input(f"{user_name} wants to join. (y=allow / n=reject): ").strip().lower()
        if cmd == "y":
            return True
        if cmd == "n":
            return False
        print("Invalid command. Enter y or n.")


def send_to_all_clients(message, sender_socket, as_bytes=True):
    """Broadcast message đến tất cả client trừ sender"""
    data = message.encode() if as_bytes else message
    with lock:
        for addr, sock in list(connected_clients.items()):
            if sock is not sender_socket:
                try:
                    sock.send(data if isinstance(data, bytes) else data.encode())
                except (BrokenPipeError, ConnectionResetError):
                    pass


def send_private_message(target_socket, message):
    """Gửi tin nhắn riêng đến 1 client"""
    try:
        target_socket.send(message.encode())
    except (BrokenPipeError, ConnectionResetError):
        pass


def kick_user(username, kicked_by=""):
    """Kick user: gửi thông báo, đóng socket, xóa khỏi danh sách"""
    if username not in username_to_addr:
        return False
    addr = username_to_addr[username]
    sock = connected_clients.get(addr)
    if sock:
        try:
            sock.send(KICKED_MESSAGE.encode())
            sock.close()
        except Exception:
            pass
    with lock:
        username_to_addr.pop(username, None)
        addr_to_username.pop(addr, None)
        connected_clients.pop(addr, None)
    return True


def manage_clients(connection_socket, addr):
    """Xử lý message từ client: /list, /kick, /ban, /leave, /private, broadcast"""
    addr_str = str(addr)
    user_name = addr_to_username.get(addr_str, "unknown")

    while True:
        try:
            raw = connection_socket.recv(BUFFER_SIZE).decode()
            if not raw:
                break
            msg_body = raw.strip()
            if not msg_body:
                continue

            prefix = f"{user_name}: "

            # /leave
            if msg_body == "/leave":
                with lock:
                    username_to_addr.pop(user_name, None)
                    addr_to_username.pop(addr_str, None)
                    connected_clients.pop(addr_str, None)
                send_to_all_clients(f"{user_name} left the chat.", connection_socket)
                try:
                    connection_socket.close()
                except Exception:
                    pass
                break

            # /list
            if msg_body == "/list":
                with lock:
                    users = list(username_to_addr.keys())
                list_msg = "Connected users: " + ", ".join(users) if users else "No other users online."
                send_private_message(connection_socket, list_msg)
                continue

            # /kick <username> (admin only)
            if msg_body.startswith("/kick "):
                if user_name != ADMIN_USERNAME:
                    send_private_message(connection_socket, "Permission denied. Admin only.")
                    continue
                parts = msg_body.split(maxsplit=2)
                if len(parts) < 2:
                    send_private_message(connection_socket, "Usage: /kick <username>")
                    continue
                target = parts[1]
                if kick_user(target):
                    send_to_all_clients(f"{target} was kicked by admin.", connection_socket)
                    send_private_message(connection_socket, f"You kicked {target}.")
                else:
                    send_private_message(connection_socket, f"User '{target}' not found.")
                continue

            # /ban <username> (admin only)
            if msg_body.startswith("/ban "):
                if user_name != ADMIN_USERNAME:
                    send_private_message(connection_socket, "Permission denied. Admin only.")
                    continue
                parts = msg_body.split(maxsplit=2)
                if len(parts) < 2:
                    send_private_message(connection_socket, "Usage: /ban <username>")
                    continue
                target = parts[1]
                banned_users.add(target)
                was_online = kick_user(target)
                send_to_all_clients(f"{target} was banned by admin.", connection_socket)
                send_private_message(connection_socket, f"You banned {target}.")
                continue

            # /private <username> <message>
            if msg_body.startswith("/private "):
                parts = msg_body.split(maxsplit=2)
                if len(parts) >= 3:
                    target_user = parts[1]
                    private_msg = parts[2]
                    if target_user in username_to_addr:
                        target_addr = username_to_addr[target_user]
                        target_sock = connected_clients.get(target_addr)
                        if target_sock:
                            send_private_message(target_sock, f"[Private] {user_name}: {private_msg}")
                            send_private_message(connection_socket, f"[To {target_user}]: {private_msg}")
                    else:
                        send_private_message(connection_socket, f"User '{target_user}' not found.")
                else:
                    send_private_message(connection_socket, "Usage: /private <username> <message>")
                continue

            # Broadcast (message thường)
            send_to_all_clients(prefix + msg_body, connection_socket)

        except (ConnectionResetError, BrokenPipeError, OSError):
            break
        except Exception:
            break

    # Client disconnect (exception hoặc /leave) - cleanup an toàn
    with lock:
        username_to_addr.pop(user_name, None)
        addr_to_username.pop(addr_str, None)
        connected_clients.pop(addr_str, None)
    try:
        send_to_all_clients(f"{user_name} left the chat.", connection_socket)
    except Exception:
        pass
    try:
        connection_socket.close()
    except Exception:
        pass


def start_server():
    """Chạy server: accept client, validate username, spawn thread"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", SERVER_PORT))  # Lắng nghe mọi interface
    server_socket.listen()
    print(f"Server listening on 0.0.0.0:{SERVER_PORT} (localhost: {SERVER_PORT})")
    print("Server is ready to welcome clients.")

    while True:
        connection_socket, addr = server_socket.accept()
        try:
            connection_socket.send(WELCOME_MESSAGE.encode())
            user_name = connection_socket.recv(BUFFER_SIZE).decode().strip()
            user_name = "".join(user_name.split())  # bỏ khoảng trắng

            if not user_name:
                connection_socket.send("Username cannot be empty.".encode())
                connection_socket.close()
                continue

            # Kiểm tra banned
            if user_name in banned_users:
                connection_socket.send(BANNED_MESSAGE.encode())
                connection_socket.close()
                continue

            # Kiểm tra trùng username
            with lock:
                if user_name in username_to_addr:
                    connection_socket.send(DUPLICATE_USERNAME_MESSAGE.encode())
                    connection_socket.close()
                    continue

            # Admin approve
            if not is_user_allowed(connection_socket, user_name):
                connection_socket.send(REJECTED_MESSAGE.encode())
                connection_socket.close()
                continue

            # Thêm vào danh sách
            with lock:
                addr_to_username[str(addr)] = user_name
                username_to_addr[user_name] = str(addr)
                connected_clients[str(addr)] = connection_socket

            print(f"{user_name} has connected.")

            # Gửi thông báo join cho mọi người (trừ user mới)
            send_to_all_clients(f"{user_name} joined the chat.", connection_socket)

            # Gửi hướng dẫn (admin thêm lệnh kick/ban)
            options = OPTIONS_MESSAGE
            if user_name == ADMIN_USERNAME:
                options += "\nAdmin commands:\n" + ADMIN_OPTIONS
            connection_socket.send(options.encode())

            t = threading.Thread(target=manage_clients, args=(connection_socket, addr))
            t.daemon = True
            t.start()

        except Exception as e:
            print(f"Error accepting client: {e}")
            try:
                connection_socket.close()
            except Exception:
                pass


if __name__ == "__main__":
    start_server()
