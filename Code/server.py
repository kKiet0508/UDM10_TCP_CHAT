# -*- coding: utf-8 -*-
"""
Server - UDM_10 Chat Console via TCP
Xử lý: login, broadcast, private message, /list, /kick, /ban, thông báo join/leave
"""

import queue
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
pending_connections = []  # [(conn, username), ...] chờ admin approve

# Lock cho thread-safe khi sửa dict
lock = threading.Lock()


def _strip_brackets(s):
    """Bỏ dấu < > nếu user gõ nhầm (vd: <kiet> -> kiet)"""
    return s.strip().strip("<>").strip()


def _resolve_username(query):
    """Tìm username thật từ query (không phân biệt hoa thường). Trả về None nếu không tìm thấy."""
    query = _strip_brackets(query).lower()
    with lock:
        for name in username_to_addr:
            if name.lower() == query:
                return name
    return None


def _print_server_list():
    """In danh sách user đang online lên console server"""
    with lock:
        users = list(username_to_addr.keys())
    msg = "Connected users: " + ", ".join(users) if users else "No users online."
    print(f"[SERVER] {msg}")


def _run_server_command(cmd):
    """Xử lý lệnh admin từ console server. Trả về True nếu đã xử lý."""
    raw = cmd.strip()
    lower = raw.lower()
    if lower in ("list", "/list"):
        _print_server_list()
        return True
    if lower.startswith("kick ") or lower.startswith("/kick "):
        target = _resolve_username(raw.split(maxsplit=1)[-1])
        if target and kick_user(target):
            print(f"[SERVER] Kicked {target}")
        else:
            print(f"[SERVER] User not found.")
        return True
    if lower.startswith("ban ") or lower.startswith("/ban "):
        target = _resolve_username(raw.split(maxsplit=1)[-1])
        if target:
            banned_users.add(target)
            kick_user(target)
            print(f"[SERVER] Banned {target}")
        else:
            print(f"[SERVER] User not found.")
        return True
    # /msg all <message> - gửi tới tất cả client
    # /msg <username> <message> - gửi tới client cụ thể
    if lower.startswith("msg ") or lower.startswith("/msg "):
        parts = raw.split(maxsplit=2)
        if len(parts) < 3:
            print("[SERVER] Usage: /msg all <message>  hoac  /msg username <message>")
            return True
        target = parts[1].strip().strip("<>")
        message = parts[2]
        msg_formatted = f"[Server] {message}"
        if target.lower() == "all":
            send_to_all_clients(msg_formatted, None)  # None = gửi tới tất cả
        else:
            target = _resolve_username(target)
            if target:
                addr = username_to_addr[target]
                sock = connected_clients.get(addr)
                if sock:
                    send_private_message(sock, msg_formatted)
                else:
                    print(f"[SERVER] User '{target}' khong ket noi.")
            else:
                print(f"[SERVER] User '{target}' not found.")
        return True
    # Không phải lệnh -> gửi broadcast tới tất cả client (server chat)
    if raw:
        send_to_all_clients(f"[Server] {raw}", None)
        return True
    return False


def _add_client(connection_socket, user_name, addr):
    """Thêm client vào chat sau khi admin approve"""
    with lock:
        addr_to_username[str(addr)] = user_name
        username_to_addr[user_name] = str(addr)
        connected_clients[str(addr)] = connection_socket
    print(f"{user_name} has connected.")
    send_to_all_clients(f"[Client] {user_name} joined the chat.", connection_socket)
    options = OPTIONS_MESSAGE
    if user_name == ADMIN_USERNAME:
        options += "\nAdmin commands:\n" + ADMIN_OPTIONS
    connection_socket.send((options + "\n").encode())
    t = threading.Thread(target=manage_clients, args=(connection_socket, addr))
    t.daemon = True
    t.start()


def send_to_all_clients(message, sender_socket=None, as_bytes=True):
    """Broadcast message tới tất cả client. sender_socket=None thì gửi tới mọi client."""
    msg = message if isinstance(message, str) else message.decode()
    if not msg.endswith("\n"):
        msg += "\n"
    data = msg.encode()
    with lock:
        for addr, sock in list(connected_clients.items()):
            if sender_socket is None or sock is not sender_socket:
                try:
                    sock.send(data)
                except (BrokenPipeError, ConnectionResetError):
                    pass


def send_private_message(target_socket, message):
    """Gửi tin nhắn riêng đến 1 client"""
    try:
        data = message if message.endswith("\n") else message + "\n"
        target_socket.send(data.encode())
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

            prefix = f"[Client] {user_name}: "

            # /leave
            if msg_body == "/leave":
                print(f"[Client] {user_name} left the chat")
                with lock:
                    username_to_addr.pop(user_name, None)
                    addr_to_username.pop(addr_str, None)
                    connected_clients.pop(addr_str, None)
                send_to_all_clients(f"[Client] {user_name} left the chat.", connection_socket)
                try:
                    connection_socket.close()
                except Exception:
                    pass
                break

            # /help
            if msg_body == "/help":
                from config import OPTIONS_MESSAGE
                send_private_message(connection_socket, OPTIONS_MESSAGE)
                continue

            # /list
            if msg_body == "/list":
                with lock:
                    users = list(username_to_addr.keys())
                list_msg = "Connected users: " + ", ".join(users) if users else "No other users online."
                print(f"[Client] {user_name} -> /list | {list_msg}")
                send_private_message(connection_socket, list_msg)
                continue

            # /kick <username> (admin only)
            if msg_body.startswith("/kick "):
                if user_name != ADMIN_USERNAME:
                    send_private_message(connection_socket, "Permission denied. Admin only.")
                    continue
                parts = msg_body.split(maxsplit=2)
                if len(parts) < 2:
                    send_private_message(connection_socket, "Usage: /kick username (vd: /kick thuong)")
                    continue
                target = _resolve_username(parts[1])
                print(f"[Client] {user_name} -> /kick {target or parts[1]}")
                if target and kick_user(target):
                    send_to_all_clients(f"[Server] {target} was kicked by admin.", connection_socket)
                    send_private_message(connection_socket, f"You kicked {target}.")
                else:
                    send_private_message(connection_socket, "User not found.")
                continue

            # /ban <username> (admin only)
            if msg_body.startswith("/ban "):
                if user_name != ADMIN_USERNAME:
                    send_private_message(connection_socket, "Permission denied. Admin only.")
                    continue
                parts = msg_body.split(maxsplit=2)
                if len(parts) < 2:
                    send_private_message(connection_socket, "Usage: /ban username (vd: /ban kiet)")
                    continue
                target = _resolve_username(parts[1])
                if not target:
                    send_private_message(connection_socket, "User not found.")
                    continue
                print(f"[Client] {user_name} -> /ban {target}")
                banned_users.add(target)
                kick_user(target)
                send_to_all_clients(f"[Server] {target} was banned by admin.", connection_socket)
                send_private_message(connection_socket, f"You banned {target}.")
                continue

            # /private username message (không phân biệt hoa thường)
            if msg_body.startswith("/private "):
                parts = msg_body.split(maxsplit=2)
                if len(parts) >= 3:
                    target_user = _resolve_username(parts[1])  # phat -> Phat
                    private_msg = parts[2]
                    if target_user:
                        target_addr = username_to_addr[target_user]
                        target_sock = connected_clients.get(target_addr)
                        if target_sock:
                            print(f"[Client] {user_name} -> /private {target_user}: {private_msg}")
                            send_private_message(target_sock, f"[Client] [Private] {user_name}: {private_msg}")
                            send_private_message(connection_socket, f"[To {target_user}]: {private_msg}")
                    else:
                        send_private_message(
                            connection_socket,
                            "User not found. Vi du: /private Phat xin chao (khong phan biet hoa thuong)",
                        )
                else:
                    send_private_message(
                        connection_socket,
                        "Usage: /private username message (vd: /private kiet xin chao)",
                    )
                continue

            # Broadcast (message thường - gồm cả /color)
            print(f"[Client] {user_name}: {msg_body}")
            send_to_all_clients(prefix + msg_body, connection_socket)

        except (ConnectionResetError, BrokenPipeError, OSError):
            print(f"[Client] {user_name} disconnected (connection lost)")
            break
        except Exception:
            print(f"[Client] {user_name} disconnected (error)")
            break

    # Client disconnect (exception hoặc /leave) - cleanup an toàn
    with lock:
        username_to_addr.pop(user_name, None)
        addr_to_username.pop(addr_str, None)
        connected_clients.pop(addr_str, None)
    try:
        send_to_all_clients(f"[Client] {user_name} left the chat.", connection_socket)
    except Exception:
        pass
    try:
        connection_socket.close()
    except Exception:
        pass


def _is_username_taken(name):
    """Kiểm tra username đã tồn tại (không phân biệt hoa thường)"""
    name_lower = name.lower()
    with lock:
        for n in username_to_addr:
            if n.lower() == name_lower:
                return True
    return False


def _is_banned(name):
    """Kiểm tra username bị ban (không phân biệt hoa thường)"""
    name_lower = name.lower()
    for n in banned_users:
        if n.lower() == name_lower:
            return True
    return False


def _accept_loop(server_socket):
    """Thread chấp nhận kết nối, thêm vào pending_connections"""
    while True:
        try:
            conn, addr = server_socket.accept()
            conn.send((WELCOME_MESSAGE.strip() + "\n").encode())
            user_name = conn.recv(BUFFER_SIZE).decode().strip()
            user_name = "".join(user_name.split())
            if not user_name:
                conn.send("Username cannot be empty.".encode())
                conn.close()
                continue
            if _is_banned(user_name):
                conn.send(BANNED_MESSAGE.encode())
                conn.close()
                continue
            if _is_username_taken(user_name):
                conn.send(DUPLICATE_USERNAME_MESSAGE.encode())
                conn.close()
                continue
            with lock:
                pending_connections.append((conn, addr, user_name))
        except Exception as e:
            if server_socket.fileno() != -1:
                print(f"Accept error: {e}")


def start_server():
    """Chạy server: accept thread + admin console loop"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", SERVER_PORT))
    server_socket.listen()
    print(f"Server listening on 0.0.0.0:{SERVER_PORT}")
    print("Chat: go message de gui tat ca. Lenh: /list /kick /ban /msg user message")

    accept_thread = threading.Thread(target=_accept_loop, args=(server_socket,), daemon=True)
    accept_thread.start()

    input_queue = queue.Queue()

    def input_loop():
        while True:
            try:
                line = input()
                input_queue.put(line)
            except EOFError:
                break

    threading.Thread(target=input_loop, daemon=True).start()

    last_pending_count = 0
    while True:
        with lock:
            pending = list(pending_connections)

        try:
            cmd = input_queue.get(timeout=0.3)
        except queue.Empty:
            if pending and len(pending) != last_pending_count:
                last_pending_count = len(pending)
                print(f"\n{pending[0][2]} wants to join. (y/n /list /kick /ban /msg): ", end="", flush=True)
            continue
        last_pending_count = 0

        if pending:
            conn, addr, user_name = pending[0]
            lower = cmd.lower().strip()
            if lower == "y":
                with lock:
                    pending_connections.remove((conn, addr, user_name))
                _add_client(conn, user_name, addr)
            elif lower == "n":
                with lock:
                    pending_connections.remove((conn, addr, user_name))
                conn.send(REJECTED_MESSAGE.encode())
                conn.close()
            else:
                _run_server_command(cmd)
        else:
            if cmd.strip():
                _run_server_command(cmd)


if __name__ == "__main__":
    start_server()
