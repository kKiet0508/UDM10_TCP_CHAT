# -*- coding: utf-8 -*-
import threading

from config import (
    WELCOME_MESSAGE,
    DUPLICATE_USERNAME_MESSAGE,
    BANNED_MESSAGE,
    ADMIN_USERNAME,
    OPTIONS_MESSAGE,
    ADMIN_OPTIONS,
    USERNAME_MAX_LEN,
    USERNAME_LINE_TOO_LONG,
)
from validation import normalize_username, validate_username, recv_line

# Luu trang thai nguoi dung
addr_to_username = {}
username_to_addr = {}
connected_clients = {}
banned_users = set()
pending_connections = []

lock = threading.Lock()


def _is_username_taken_unlocked(name: str) -> bool:
    nl = name.lower()
    for n in username_to_addr:
        if n.lower() == nl:
            return True
    return False


def _is_pending_username_unlocked(name: str) -> bool:
    nl = name.lower()
    for _, _, u in pending_connections:
        if u.lower() == nl:
            return True
    return False


def _resolve_username(query):
    """Tim ten user chinh xac, khong phan biet hoa thuong."""
    query = query.strip().strip("<>").lower()
    with lock:
        for name in username_to_addr:
            if name.lower() == query:
                return name
    return None


def _is_username_taken(name):
    """Kiem tra ten da ton tai chua (co lock)."""
    with lock:
        return _is_username_taken_unlocked(name)


def _is_banned(name):
    """Kiem tra user co bi ban khong."""
    for n in banned_users:
        if n.lower() == name.lower():
            return True
    return False


def _add_client(connection_socket, user_name, addr):
    """Them client vao phong chat va bat dau xu ly tin nhan."""
    with lock:
        addr_to_username[str(addr)] = user_name
        username_to_addr[user_name] = str(addr)
        connected_clients[str(addr)] = connection_socket

    print(f"{user_name} da ket noi.")

    import server_channels as ch
    from server_control import manage_clients

    ch.send_to_all_clients(f"[Client] {user_name} vua vao phong chat.", connection_socket)

    options = OPTIONS_MESSAGE
    if user_name == ADMIN_USERNAME:
        options += "\nAdmin commands:\n" + ADMIN_OPTIONS
    connection_socket.send((options + "\n").encode())
    t = threading.Thread(target=manage_clients, args=(connection_socket, addr))
    t.daemon = True
    t.start()


def _accept_loop(server_socket):
    """Vong lap chap nhan ket noi moi tu client."""
    max_raw = USERNAME_MAX_LEN + 64
    while True:
        try:
            conn, addr = server_socket.accept()
            conn.send((WELCOME_MESSAGE.strip() + "\n").encode("utf-8"))
            raw_line = recv_line(conn, max_raw)
            if raw_line is None:
                try:
                    conn.send((USERNAME_LINE_TOO_LONG + "\n").encode("utf-8"))
                except Exception:
                    pass
                conn.close()
                continue

            user_name = normalize_username(raw_line)
            ok, err_msg = validate_username(user_name)
            if not ok:
                try:
                    conn.send((err_msg + "\n").encode("utf-8"))
                except Exception:
                    pass
                conn.close()
                continue

            if _is_banned(user_name):
                conn.send(BANNED_MESSAGE.encode())
                conn.close()
                continue

            with lock:
                if _is_username_taken_unlocked(user_name) or _is_pending_username_unlocked(user_name):
                    conn.send(DUPLICATE_USERNAME_MESSAGE.encode())
                    conn.close()
                    continue
                pending_connections.append((conn, addr, user_name))
        except Exception as e:
            if server_socket.fileno() != -1:
                print(f"Loi chap nhan ket noi: {e}")
