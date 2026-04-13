# -*- coding: utf-8 -*-
"""
Kiem tra hop le username / do dai dong; doc mot dong tu socket (tranh recv 1 lan bi cat).
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

from config import (
    USERNAME_MIN_LEN,
    USERNAME_MAX_LEN,
    CHAT_LINE_MAX_LEN,
    INVALID_USERNAME_EMPTY,
    INVALID_USERNAME_SHORT,
    INVALID_USERNAME_LONG,
    INVALID_USERNAME_CHARS,
    LINE_TOO_LONG_MESSAGE,
)


# Chu cai Unicode (ten tieng Viet), so, _, -, ., va mot khoang trang giua cac tu
_USERNAME_PATTERN = re.compile(r"^[\w\-. ]+$", re.UNICODE)


def normalize_username(raw: str) -> str:
    """Chuan hoa: bo khoang dau/cuoi, gop khoang trang giua thanh mot."""
    if raw is None:
        return ""
    return " ".join(raw.strip().split())


def validate_username(name: str) -> Tuple[bool, str]:
    """
    Tra ve (True, "") neu hop le.
    Tra ve (False, thong_bao) neu khong hop le (thong_bao gui cho user).
    """
    if not name:
        return False, INVALID_USERNAME_EMPTY
    if len(name) < USERNAME_MIN_LEN:
        return False, INVALID_USERNAME_SHORT
    if len(name) > USERNAME_MAX_LEN:
        return False, INVALID_USERNAME_LONG
    if not _USERNAME_PATTERN.fullmatch(name):
        return False, INVALID_USERNAME_CHARS
    return True, ""


def validate_chat_line(text: str) -> Tuple[bool, str]:
    if len(text) > CHAT_LINE_MAX_LEN:
        return False, LINE_TOO_LONG_MESSAGE
    return True, ""


def recv_line(conn, max_line_length: int, chunk_size: int = 1024) -> Optional[str]:
    """
    Doc mot dong ket thuc bang \\n (UTF-8).
    Tra ve None neu dong qua dai (> max_line_length), mat ket noi, hoac loi giao thuc.
    """
    buf = bytearray()
    while True:
        if len(buf) > max_line_length + 1:
            return None
        chunk = conn.recv(chunk_size)
        if not chunk:
            if not buf:
                return None
            line = bytes(buf).decode("utf-8", errors="replace").strip("\r\n")
            return line if len(line) <= max_line_length else None
        buf.extend(chunk)
        if b"\n" in buf:
            idx = buf.index(b"\n")
            if idx > max_line_length:
                return None
            line = bytes(buf[:idx]).decode("utf-8", errors="replace").strip("\r")
            return line if len(line) <= max_line_length else None
