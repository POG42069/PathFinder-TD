"""
level.py - Định nghĩa 3 màn chơi
Môn: IT003 - Cấu trúc dữ liệu và Giải thuật - UIT

Mỗi màn có:
    - Tên và mô tả
    - Điểm spawn và base khác nhau
    - Vật cản cố định khác nhau
    - Màu sắc chủ đề riêng
"""

from settings import GRID_ROWS, GRID_COLS



LEVELS = [
    {
        'id':    1,
        'name':  'Bãi Chiến Trường (Ma Trận)',
        'desc':  'Bãi đất trống rộng lớn\nHãy tự do xây tháp để ép quái đi theo ý muốn!',
        'difficulty': 'Vô hạn',
        'diff_color': (80, 210, 80),

        'spawn':  (0, 0),
        'base':   (GRID_ROWS - 1, GRID_COLS - 1),

        'obstacles': [
            (0, GRID_COLS - 1),
            (GRID_ROWS - 1, 0),
            (1, GRID_COLS - 1),
            (GRID_ROWS - 1, 1),
        ],

        'theme_color': (30, 60, 40),
        'sky_color':   (40, 80, 140),

        'starting_gold': 250,
        'starting_hp':   20,
    }
]


def get_level(level_id):
    """
    Lấy dữ liệu màn chơi theo ID (1-based).

    Trả về:
        dict hoặc None nếu không tồn tại.
    """
    for lv in LEVELS:
        if lv['id'] == level_id:
            return lv
    return None


def get_all_levels():
    """Trả về danh sách tất cả màn chơi."""
    return LEVELS


def validate_level(level_data):
    """
    Kiểm tra màn chơi có hợp lệ không:
    - Spawn và base nằm trong lưới
    - Không trùng nhau
    - Có đường đi từ spawn đến base (không bị vật cản chặn hết)

    Trả về:
        (bool, str): (is_valid, error_message)
    """
    spawn = level_data.get('spawn')
    base  = level_data.get('base')
    obs   = level_data.get('obstacles', [])

    if not spawn or not base:
        return False, "Thiếu spawn hoặc base"

    sr, sc = spawn
    br, bc = base

    if not (0 <= sr < GRID_ROWS and 0 <= sc < GRID_COLS):
        return False, "Spawn ngoài lưới"
    if not (0 <= br < GRID_ROWS and 0 <= bc < GRID_COLS):
        return False, "Base ngoài lưới"
    if spawn == base:
        return False, "Spawn trùng Base"
    if spawn in obs or base in obs:
        return False, "Spawn/Base trùng vật cản"

    from bfs import has_path
    grid = [[0]*GRID_COLS for _ in range(GRID_ROWS)]
    grid[sr][sc] = 2
    grid[br][bc] = 3
    for (r, c) in obs:
        if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
            grid[r][c] = 4

    if not has_path(grid, spawn, base, GRID_ROWS, GRID_COLS):
        return False, "Vật cản chặn hết đường đi"

    return True, "OK"
