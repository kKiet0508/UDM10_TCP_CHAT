# -*- coding: utf-8 -*-
"""
Diem vao chay client: khoi tao 2 luong gui va nhan tin nhan song song.
"""
import threading

from client_display import receive_message
from client_transport import connect_client_socket, send_message


def main():
    client_socket = connect_client_socket()
    login_state = {"need_username": True}
    print("Nhap ten dang nhap (3-32 ky tu: chu, so, _, -, ., khoang trong giua tu).")

    # Luong nhan tin nhan tu server
    recv_thread = threading.Thread(target=receive_message, args=(client_socket,), daemon=True)
    # Luong gui tin nhan len server (gui username hop le truoc khi chat)
    send_thread = threading.Thread(target=send_message, args=(client_socket, login_state), daemon=True)

    recv_thread.start()
    send_thread.start()
    recv_thread.join()
    send_thread.join()


if __name__ == "__main__":
    main()
