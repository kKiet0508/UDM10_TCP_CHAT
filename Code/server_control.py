
"""
Xu ly lenh cua tung client, quan ly console admin, khoi dong server.
"""
import queue
import socket
import threading

from config import (
    SERVER_PORT,
    ADMIN_USERNAME,
    BUFFER_SIZE,
    REJECTED_MESSAGE,
    OPTIONS_MESSAGE,
)
import server_registry as reg
import server_channels as ch


def manage_clients(connection_socket, addr):
    """Xu ly tin nhan va lenh gui len tu mot client."""
    addr_str  = str(addr)
    user_name = reg.addr_to_username.get(addr_str, "unknown")

    while True:
        try:
            raw = connection_socket.recv(BUFFER_SIZE).decode()
            if not raw:
                break
            msg_body = raw.strip()
            if not msg_body:
                continue

            # Thoat khoi phong chat
            if msg_body == "/leave":
                print(f"[Client] {user_name} da roi phong chat")
                with reg.lock:
                    reg.username_to_addr.pop(user_name, None)
                    reg.addr_to_username.pop(addr_str, None)
                    reg.connected_clients.pop(addr_str, None)
                ch.send_to_all_clients(f"[Client] {user_name} da roi phong chat.", connection_socket)
                connection_socket.close()
                break

            # Xem huong dan
            if msg_body == "/help":
                ch.send_private_message(connection_socket, OPTIONS_MESSAGE)
                continue

            # Xem danh sach user online
            if msg_body == "/list":
                with reg.lock:
                    users = list(reg.username_to_addr.keys())
                list_msg = "Nguoi dung online: " + ", ".join(users) if users else "Khong co ai online."
                ch.send_private_message(connection_socket, list_msg)
                continue

            # Kick user (chi admin)
            if msg_body.startswith("/kick "):
                if user_name != ADMIN_USERNAME:
                    ch.send_private_message(connection_socket, "Ban khong co quyen dung lenh nay.")
                    continue
                parts = msg_body.split(maxsplit=1)
                target = reg._resolve_username(parts[1])
                if target and ch.kick_user(target):
                    ch.send_to_all_clients(f"[Server] {target} bi kick boi admin.", connection_socket)
                    ch.send_private_message(connection_socket, f"Da kick {target}.")
                else:
                    ch.send_private_message(connection_socket, "Khong tim thay user.")
                continue

            # Ban user (chi admin)
            if msg_body.startswith("/ban "):
                if user_name != ADMIN_USERNAME:
                    ch.send_private_message(connection_socket, "Ban khong co quyen dung lenh nay.")
                    continue
                parts = msg_body.split(maxsplit=1)
                target = reg._resolve_username(parts[1])
                if not target:
                    ch.send_private_message(connection_socket, "Khong tim thay user.")
                    continue
                reg.banned_users.add(target)
                ch.kick_user(target)
                ch.send_to_all_clients(f"[Server] {target} bi ban boi admin.", connection_socket)
                ch.send_private_message(connection_socket, f"Da ban {target}.")
                continue

            # Tin nhan rieng
            if msg_body.startswith("/private "):
                parts = msg_body.split(maxsplit=2)
                if len(parts) >= 3:
                    target_user = reg._resolve_username(parts[1])
                    private_msg = parts[2]
                    if target_user:
                        target_addr = reg.username_to_addr[target_user]
                        target_sock = reg.connected_clients.get(target_addr)
                        if target_sock:
                            ch.send_private_message(target_sock, f"[Rieng] {user_name}: {private_msg}")
                            ch.send_private_message(connection_socket, f"[Den {target_user}]: {private_msg}")
                    else:
                        ch.send_private_message(connection_socket, "Khong tim thay user.")
                else:
                    ch.send_private_message(connection_socket, "Cu phap: /private username noi_dung")
                continue

            # Tin nhan thuong broadcast
            print(f"[Client] {user_name}: {msg_body}")
            ch.send_to_all_clients(f"[Client] {user_name}: {msg_body}", connection_socket)

        except (ConnectionResetError, BrokenPipeError, OSError):
            print(f"[Client] {user_name} mat ket noi")
            break

    with reg.lock:
        reg.username_to_addr.pop(user_name, None)
        reg.addr_to_username.pop(addr_str, None)
        reg.connected_clients.pop(addr_str, None)
    try:
        ch.send_to_all_clients(f"[Client] {user_name} da roi phong chat.", connection_socket)
    except Exception:
        pass
    try:
        connection_socket.close()
    except Exception:
        pass


def start_server():
    """Khoi dong server, lang nghe ket noi va quan ly admin console."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", SERVER_PORT))
    server_socket.listen()
    print(f"Server dang chay tren cong {SERVER_PORT}")
    print("Lenh admin: /list /kick /ban")

    # Luong chap nhan ket noi moi
    accept_thread = threading.Thread(target=reg._accept_loop, args=(server_socket,), daemon=True)
    accept_thread.start()

    input_queue = queue.Queue()

    def input_loop():
        while True:
            try:
                input_queue.put(input())
            except EOFError:
                break

    threading.Thread(target=input_loop, daemon=True).start()

    while True:
        with reg.lock:
            pending = list(reg.pending_connections)

        try:
            cmd = input_queue.get(timeout=0.3)
        except queue.Empty:
            if pending:
                print(f"\n{pending[0][2]} muon vao phong. Chap nhan? (y/n): ", end="", flush=True)
            continue

        if pending:
            conn, addr, user_name = pending[0]
            if cmd.lower().strip() == "y":
                with reg.lock:
                    reg.pending_connections.remove((conn, addr, user_name))
                reg._add_client(conn, user_name, addr)
            elif cmd.lower().strip() == "n":
                with reg.lock:
                    reg.pending_connections.remove((conn, addr, user_name))
                conn.send(REJECTED_MESSAGE.encode())
                conn.close()
            else:
                _run_admin_command(cmd)
        else:
            if cmd.strip():
                _run_admin_command(cmd)


def _run_admin_command(cmd):
    """Xu ly lenh admin nhap tu console server."""
    raw   = cmd.strip()
    lower = raw.lower()

    if lower in ("list", "/list"):
        with reg.lock:
            users = list(reg.username_to_addr.keys())
        print("Online: " + ", ".join(users) if users else "Khong co ai online.")
        return

    if lower.startswith(("kick ", "/kick ")):
        target = reg._resolve_username(raw.split(maxsplit=1)[-1])
        if target and ch.kick_user(target):
            print(f"Da kick {target}")
        else:
            print("Khong tim thay user.")
        return

    if lower.startswith(("ban ", "/ban ")):
        target = reg._resolve_username(raw.split(maxsplit=1)[-1])
        if target:
            reg.banned_users.add(target)
            ch.kick_user(target)
            print(f"Da ban {target}")
        else:
            print("Khong tim thay user.")
        return

    # Gui tin nhan tu server toi tat ca
    ch.send_to_all_clients(f"[Server] {raw}", None)
