import threading

from config import (
    BUFFER_SIZE,
    WELCOME_MESSAGE,
    DUPLICATE_USERNAME_MESSAGE,
    BANNED_MESSAGE,
    ADMIN_USERNAME,
    OPTIONS_MESSAGE,
    ADMIN_OPTIONS,
)

# Luu trang thai nguoi dung
addr_to_username    = {}
username_to_addr    = {}
connected_clients   = {}
banned_users        = set()
pending_connections = []

lock = threading.Lock()


def _resolve_username(query):
    """Tim ten user chinh xac, khong phan biet hoa thuong."""
    query = query.strip().strip("<>").lower()
    with lock:
        for name in username_to_addr:
            if name.lower() == query:   
                return name
    return None


def _is_username_taken(name):
    """Kiem tra ten da ton tai chua."""
    with lock:
        for n in username_to_addr:
            if n.lower() == name.lower():   
                return True
    return False


def _is_banned(name):
    """Kiem tra user co bi ban khong."""
    for n in banned_users:
        if n.lower() == name.lower():
            return True
    return False


def _add_client(connection_socket, user_name, addr):
    """Them client vao phong chat va bat dau xu ly tin nhan."""
    with lock:
        addr_to_username[str(addr)]  = user_name
        username_to_addr[user_name]  = str(addr)
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
    while True:
        try:
            conn, addr = server_socket.accept()
            conn.send((WELCOME_MESSAGE.strip() + "\n").encode())  
            user_name = conn.recv(BUFFER_SIZE).decode().strip()
            if not user_name:
                conn.send("Ten nguoi dung khong duoc de trong.".encode()) 
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
                print(f"Loi chap nhan ket noi: {e}") 
