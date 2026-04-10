
"""
Gui tin nhan toi tat ca, gui tin rieng giua 2 nguoi, kick user khoi phong.
"""
from config import KICKED_MESSAGE
import server_registry as reg


def send_to_all_clients(message, sender_socket=None):
    """Gui tin nhan toi tat ca user, tru nguoi gui."""
    msg = message if isinstance(message, str) else message.decode()
    if not msg.endswith("\n"):
        msg += "\n"
    data = msg.encode()
    with reg.lock:
        for addr, sock in list(reg.connected_clients.items()):
            if sender_socket is None or sock is not sender_socket:
                try:
                    sock.send(data)
                except (BrokenPipeError, ConnectionResetError):
                    pass


def send_private_message(target_socket, message):
    """Gui tin nhan rieng toi mot user cu the."""
    try:
        data = message if message.endswith("\n") else message + "\n"
        target_socket.send(data.encode())
    except (BrokenPipeError, ConnectionResetError):
        pass


def kick_user(username):
    """Kick user ra khoi phong chat va dong ket noi."""
    if username not in reg.username_to_addr:
        return False
    addr = reg.username_to_addr[username]
    sock = reg.connected_clients.get(addr)
    if sock:
        try:
            sock.send(KICKED_MESSAGE.encode())
            sock.close()
        except Exception:
            pass
    with reg.lock:
        reg.username_to_addr.pop(username, None)
        reg.addr_to_username.pop(addr, None)
        reg.connected_clients.pop(addr, None)
    return True
