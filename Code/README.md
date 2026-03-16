# UDM_10 - Chat Console via TCP

Ứng dụng chat console qua TCP. Toàn bộ chức năng điều khiển qua command line.

## Yêu cầu

- Python 3.7+
- `colorama` (cho màu sắc trên client)

## Cài đặt

```bash
pip install -r requirements.txt
```

## Cách chạy

### 1. Chạy Server

```bash
python server.py
```

Server lắng nghe trên `0.0.0.0:1234` (mặc định). Khi có client kết nối, admin nhập `y` hoặc `n` để chấp nhận/từ chối.

### 2. Chạy Client

Trên cùng máy (localhost):

```bash
python client.py
```

Nếu server chạy trên máy khác, sửa `SERVER_HOST` trong `config.py` thành IP của máy server.

### 3. Luồng sử dụng

1. Client kết nối → nhận "Welcome... enter your username"
2. Gõ **username** rồi Enter
3. Admin server nhập `y` để cho vào / `n` để từ chối
4. Sau khi vào chatroom, gõ message hoặc dùng lệnh

## Lệnh (Commands)

| Lệnh | Mô tả |
|------|-------|
| `/list` | Liệt kê clients đang kết nối |
| `/private <user> <msg>` | Gửi tin nhắn riêng |
| `/color <màu> <msg>` | Gửi tin nhắn có màu (red, green, yellow, blue, magenta, cyan, white) |
| `/leave` | Rời chatroom |

**Admin only** (username = `admin`):

| Lệnh | Mô tả |
|------|-------|
| `/kick <username>` | Kick user ra khỏi chat |
| `/ban <username>` | Ban user (không cho đăng nhập lại) |

## Cấu trúc project

```
Code/
├── config.py      # Hằng số, port, messages
├── server.py      # Server TCP
├── client.py      # Client TCP
├── requirements.txt
└── README.md
```

## Cấu hình

Sửa `config.py` để đổi:

- `SERVER_PORT`: Port server (mặc định 1234)
- `SERVER_HOST`: Địa chỉ server cho client (mặc định 127.0.0.1)
- `ADMIN_USERNAME`: User có quyền kick/ban (mặc định "admin")
