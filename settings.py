"""
settings.py - Cấu hình và hằng số toàn cục cho PathFinder TD
Môn: IT003 - Cấu trúc dữ liệu và Giải thuật - UIT
"""

import os

# ════════════════════════════════════════════════════════
#  CỬA SỔ & FPS
# ════════════════════════════════════════════════════════
WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE  = "PathFinder TD - BFS Tower Defense"
FPS = 60

# ════════════════════════════════════════════════════════
#  LƯỚI BẢN ĐỒ (GRID)
# ════════════════════════════════════════════════════════
CELL_SIZE   = 64          # Kích thước mỗi ô (pixel)
GRID_COLS   = 15          # Số cột
GRID_ROWS   = 10          # Số hàng
GRID_OFFSET_X = 0
GRID_OFFSET_Y = 80        # Dưới HUD bar
GRID_WIDTH  = GRID_COLS * CELL_SIZE   # 960 px
GRID_HEIGHT = GRID_ROWS * CELL_SIZE   # 640 px

# ════════════════════════════════════════════════════════
#  LAYOUT MÀN HÌNH
# ════════════════════════════════════════════════════════
HUD_HEIGHT   = 80
PANEL_WIDTH  = WINDOW_WIDTH - GRID_WIDTH   # 320 px
PANEL_X      = GRID_WIDTH                  # 960

# ════════════════════════════════════════════════════════
#  TRẠNG THÁI Ô LƯỚI
# ════════════════════════════════════════════════════════
CELL_EMPTY    = 0   # Trống, đi được, xây được
CELL_BLOCKED  = 1   # Tháp (chặn đường BFS)
CELL_SPAWN    = 2   # Điểm xuất hiện quái
CELL_BASE     = 3   # Căn cứ (đích đến)
CELL_OBSTACLE = 4   # Địa hình cố định (không xây, BFS không đi được)

# ════════════════════════════════════════════════════════
#  TRẠNG THÁI GAME
# ════════════════════════════════════════════════════════
STATE_MENU         = 'menu'
STATE_LEVEL_SELECT = 'level_select'
STATE_PLAYING      = 'playing'
STATE_PAUSED       = 'paused'
STATE_GAME_OVER    = 'game_over'
STATE_VICTORY      = 'victory'
STATE_EDITOR       = 'editor'
STATE_HIGHSCORE    = 'highscore'

# ════════════════════════════════════════════════════════
#  BẢNG MÀU
# ════════════════════════════════════════════════════════
# Nền
C_BG         = (12, 16, 28)
C_HUD_BG     = (18, 22, 40)
C_PANEL_BG   = (14, 18, 32)
C_PANEL_BORDER = (40, 60, 100)

# Ô lưới
C_GRASS      = (200, 140, 50)      # Màu cam đất sáng
C_GRASS_ALT  = (190, 130, 45)      # Màu cam đất tối chút
C_PATH_SHOW  = (190, 150, 70)      # Không còn dùng, giữ lại để tương thích biến
C_SPAWN_CLR  = (220, 60, 60)
C_BASE_CLR   = (60, 120, 255)
C_OBSTACLE   = (55, 55, 65)
C_GRID_LINE  = (35, 75, 35)
C_HIGHLIGHT  = (255, 255, 100, 80) # Hover khi xây tháp
C_INVALID    = (255, 60, 60, 80)   # Vị trí không hợp lệ

# UI chung
C_WHITE      = (255, 255, 255)
C_BLACK      = (0, 0, 0)
C_GOLD       = (255, 200, 50)
C_RED        = (220, 55, 55)
C_GREEN      = (60, 210, 60)
C_BLUE       = (60, 140, 255)
C_PURPLE     = (175, 100, 235)
C_GRAY       = (120, 125, 135)
C_DARK_GRAY  = (55, 58, 68)

# HP bar
C_HP_FULL    = (60, 220, 80)
C_HP_MED     = (230, 200, 40)
C_HP_LOW     = (230, 60, 60)

# ════════════════════════════════════════════════════════
#  DỮ LIỆU THÁP (TOWER)
# ════════════════════════════════════════════════════════
TOWER_TYPES = ['archer', 'cannon', 'mage']

TOWER_DATA = {
    'archer': {
        'name':        'Xạ Thủ',
        'desc':        'Bắn nhanh, ổn định\nPhù hợp mọi tình huống',
        'damage':      18,
        'range':       3.0,        # tầm tính bằng số ô
        'fire_rate':   1.5,        # lần bắn / giây
        'cost':        50,
        'sell_value':  30,
        'color':       (80, 210, 110),
        'accent':      (40, 160, 80),
        'bullet_color':(255, 235, 60),
        'bullet_speed': 6.0,       # ô / giây
        'bullet_size':  5,
        'splash_radius': 0,        # không có AOE
    },
    'cannon': {
        'name':        'Đại Bác',
        'desc':        'Sát thương cao nhất\nBắn chậm, AOE nhỏ',
        'damage':      70,
        'range':       2.5,
        'fire_rate':   0.45,
        'cost':        100,
        'sell_value':  60,
        'color':       (170, 170, 185),
        'accent':      (110, 110, 125),
        'bullet_color':(90, 90, 100),
        'bullet_speed': 4.5,
        'bullet_size':  8,
        'splash_radius': 0.6,      # AOE 0.6 ô
    },
    'mage': {
        'name':        'Pháp Sư',
        'desc':        'Tầm bắn xa nhất\nHiệu ứng phép thuật',
        'damage':      32,
        'range':       4.5,
        'fire_rate':   0.8,
        'cost':        125,
        'sell_value':  75,
        'color':       (165, 85, 240),
        'accent':      (110, 40, 180),
        'bullet_color':(225, 130, 255),
        'bullet_speed': 7.0,
        'bullet_size':  7,
        'splash_radius': 0,
    },
}

# ════════════════════════════════════════════════════════
#  DỮ LIỆU QUÁI (ENEMY)
# ════════════════════════════════════════════════════════
ENEMY_DATA = {
    'goblin': {
        'name':    'Quỷ Lùn',
        'hp':      90,
        'speed':   2.8,         # ô / giây
        'reward':  10,          # vàng khi giết
        'damage':  1,           # máu base mất khi đến
        'color':   (75, 210, 85),
        'outline': (30, 130, 40),
        'size':    16,          # bán kính vẽ
    },
    'orc': {
        'name':    'Orc Chiến Binh',
        'hp':      260,
        'speed':   1.7,
        'reward':  25,
        'damage':  2,
        'color':   (200, 85, 55),
        'outline': (130, 40, 20),
        'size':    22,
    },
    'troll': {
        'name':    'Quái Khổng Lồ',
        'hp':      700,
        'speed':   1.0,
        'reward':  60,
        'damage':  5,
        'color':   (85, 145, 190),
        'outline': (40, 80, 120),
        'size':    30,
    },
}

# ════════════════════════════════════════════════════════
#  ĐỊNH NGHĨA WAVE
#  Mỗi entry tuple: (loại_quái, số_lượng, khoảng cách spawn giây)
# ════════════════════════════════════════════════════════
WAVE_DEFINITIONS = [
    # Wave 1 – Khởi động
    [('goblin', 6,  1.5)],
    # Wave 2
    [('goblin', 10, 1.2)],
    # Wave 3
    [('goblin', 8, 1.0), ('orc', 2, 3.0)],
    # Wave 4
    [('goblin', 10, 0.9), ('orc', 4, 2.0)],
    # Wave 5
    [('orc', 6, 1.5), ('goblin', 6, 0.8)],
    # Wave 6
    [('orc', 8, 1.2), ('troll', 1, 5.0)],
    # Wave 7
    [('goblin', 14, 0.7), ('orc', 5, 1.0), ('troll', 2, 4.0)],
    # Wave 8
    [('orc', 10, 0.9), ('troll', 3, 3.0)],
    # Wave 9
    [('goblin', 18, 0.55), ('orc', 8, 0.8), ('troll', 3, 3.0)],
    # Wave 10 – Boss Wave
    [('troll', 6, 2.0), ('orc', 12, 0.7), ('goblin', 20, 0.4)],
]

TOTAL_WAVES       = len(WAVE_DEFINITIONS)
WAVE_BREAK_TIME   = 5.0    # giây nghỉ giữa các wave

# ════════════════════════════════════════════════════════
#  CÂN BẰNG GAME
# ════════════════════════════════════════════════════════
STARTING_GOLD       = 150
STARTING_HP         = 20
KILL_SCORE          = 10
WAVE_BONUS_SCORE    = 100
HP_LOSS_PENALTY     = 30

# ════════════════════════════════════════════════════════
#  ĐƯỜNG DẪN TÀI NGUYÊN
# ════════════════════════════════════════════════════════
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
SAVES_DIR  = os.path.join(BASE_DIR, 'saves')
MAPS_DIR   = os.path.join(BASE_DIR, 'maps')
