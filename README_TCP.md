# 💬 TCP Chat Application (CLI)

> Ứng dụng chat đơn giản sử dụng TCP Socket trong Python, chạy trên Command Line theo mô hình Client - Server.

---

## 📐 Mô hình hoạt động

```text
Client ⇄ Server ⇄ Client
           │
    Broadcast / Private
```

* Server xử lý kết nối và quản lý user
* Client gửi và nhận tin nhắn

---

## 🔧 Tính năng

* Kết nối TCP giữa client và server
* Hỗ trợ nhiều client cùng lúc
* Gửi tin nhắn tới tất cả (broadcast)
* Nhắn tin riêng giữa các user
* Kiểm tra username hợp lệ
* Hỗ trợ admin (kick / ban user)
* Hiển thị tin nhắn có màu

---

## 🚀 Cách chạy

### 1. Chạy Server

```bash
python Code/server.py
```

### 2. Chạy Client (mở nhiều terminal)

```bash
python Code/client.py
```

---

## 👤 Đăng nhập

* Nhập username khi kết nối
* Độ dài: 3–32 ký tự
* Không được trùng với user khác

---

## 📜 Lệnh sử dụng

### Client

```text
/list                 Xem danh sách user online
/private user msg     Nhắn tin riêng
/color red hello      Gửi tin nhắn có màu
/leave                Thoát chat
/help                 Xem hướng dẫn
```

### Admin (username = admin)

```text
/kick user            Đá user khỏi phòng
/ban user             Cấm user
```

---

## 📁 Cấu trúc project

```text
.
├── Code/
│   ├── client.py               # Chạy client
│   ├── client_display.py       # Nhận và hiển thị tin nhắn
│   ├── client_transport.py     # Kết nối server và gửi dữ liệu
│   ├── server.py               # Chạy server
│   ├── server_control.py       # Xử lý lệnh và logic server
│   ├── server_registry.py      # Quản lý danh sách user
│   ├── server_channels.py      # Broadcast và private message
│   ├── validation.py           # Kiểm tra dữ liệu đầu vào
│   └── config.py               # Cấu hình hệ thống
├── Docx/                       # Tài liệu báo cáo
├── Extra/                      # Tài liệu tham khảo
├── PPTX/                       # Slide thuyết trình
├── README_TCP.md
└── TCP_CHAT_CMD.xlsx
```


---

## ⚙️ Cấu hình

Trong `Code/config.py`:

```python
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 1234
```

---

## ⚠️ Lưu ý

* Chạy server trước khi chạy client
* Nếu không kết nối được → kiểm tra IP và port
* Tài khoản admin: `admin`

---


