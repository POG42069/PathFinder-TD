"""
font_manager.py - Quản lý font hỗ trợ tiếng Việt đầy đủ
Môn: IT003 - Cấu trúc dữ liệu và Giải thuật - UIT

Vấn đề: pygame.font.SysFont('Arial') trên Windows không render
         đúng dấu tiếng Việt (ă, â, ê, ơ, ư, thanh điệu...).

Giải pháp: Dùng pygame.font.Font() với đường dẫn tuyệt đối đến file
           .ttf của Segoe UI – font mặc định của Windows có hỗ trợ
           Unicode / tiếng Việt đầy đủ.
"""

import os
import pygame

# ── Danh sách font ưu tiên (thường / bold) ──────────────────────
_REGULAR_CANDIDATES = [
    r"C:\Windows\Fonts\segoeui.ttf",   # Segoe UI – tốt nhất
    r"C:\Windows\Fonts\tahoma.ttf",    # Tahoma
    r"C:\Windows\Fonts\verdana.ttf",   # Verdana
    r"C:\Windows\Fonts\arial.ttf",     # Arial (fallback)
]

_BOLD_CANDIDATES = [
    r"C:\Windows\Fonts\segoeuib.ttf",  # Segoe UI Bold
    r"C:\Windows\Fonts\tahomabd.ttf",  # Tahoma Bold
    r"C:\Windows\Fonts\verdanab.ttf",  # Verdana Bold
    r"C:\Windows\Fonts\arialbd.ttf",   # Arial Bold (fallback)
]

# ── Cache (size, bold) → Font ────────────────────────────────────
_cache: dict = {}
_path_regular: str | None = None
_path_bold:    str | None = None
_initialized   = False


def init():
    """
    Khởi tạo font manager.
    **Phải gọi sau pygame.init() và pygame.display.set_mode().**
    """
    global _path_regular, _path_bold, _initialized

    for p in _REGULAR_CANDIDATES:
        if os.path.exists(p):
            _path_regular = p
            break

    for p in _BOLD_CANDIDATES:
        if os.path.exists(p):
            _path_bold = p
            break

    _initialized = True
    print(f"[FontManager] Regular: {_path_regular}")
    print(f"[FontManager] Bold   : {_path_bold}")


def get(size: int, bold: bool = False) -> pygame.font.Font:
    """
    Trả về Font hỗ trợ tiếng Việt với kích thước và style yêu cầu.

    Font được cache để tránh tạo lại mỗi frame.

    Tham số:
        size (int) : Kích thước (pt).
        bold (bool): True → bold.

    Trả về:
        pygame.font.Font
    """
    if not _initialized:
        init()

    key = (size, bold)
    if key in _cache:
        return _cache[key]

    # Chọn đường dẫn
    if bold and _path_bold:
        path = _path_bold
    elif _path_regular:
        path = _path_regular
    else:
        path = None

    if path:
        font = pygame.font.Font(path, size)
    else:
        # Fallback cuối cùng
        font = pygame.font.SysFont(None, size, bold=bold)

    _cache[key] = font
    return font


def clear_cache():
    """Xóa cache font (gọi khi đổi resolution)."""
    _cache.clear()
