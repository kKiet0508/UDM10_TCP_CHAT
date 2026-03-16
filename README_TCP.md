# 💬 Lập Trình Mạng - TCP CHAT CMD

> **Project:** UDM_10  
> **Language:** Python  
> **Mô hình:** Client-Server TCP qua giao diện Command Line

---

## 📐 Mô hình hoạt động

```
[Client 1] ──┐
[Client 2] ──┤── TCP ──► [Server] ──► Broadcast tin nhắn tới tất cả client
[Client 3] ──┘
```

---

## 🔧 Tính năng

| Tính năng | Mô tả |
|-----------|-------|
| **TCP Connection** | Kết nối ổn định giữa Client và Server |
| **Multi-client** | Server xử lý nhiều client cùng lúc |
| **Broadcast** | Tin nhắn từ 1 client gửi tới tất cả |
| **CMD Interface** | Giao diện dòng lệnh đơn giản |
| Còn |  |

---

## 🚀 Cách chạy

### Chạy Server trước
```bash
python server.py
```

### Chạy Client (mở nhiều terminal)
```bash
python client.py
```

---

## 📁 Cấu trúc project



---

## 💡 Kiến thức áp dụng

- **TCP Socket** - Lập trình mạng tầng Transport
- **Multi-threading** - Xử lý nhiều client đồng thời
- **Client-Server Model** - Mô hình mạng cơ bản
