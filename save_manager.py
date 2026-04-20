"""
save_manager.py - Quản lý lưu điểm cao và dữ liệu game
Môn: IT003 - Cấu trúc dữ liệu và Giải thuật - UIT
"""

import json
import os
from settings import SAVES_DIR


# ════════════════════════════════════════════════════════════════
#  CẤU TRÚC DỮ LIỆU
# ════════════════════════════════════════════════════════════════

_DEFAULT_SAVE = {
    "highscores": {
        "1": [],   # List of [score, timestamp] cho level 1
        "2": [],
        "3": [],
    },
    "unlocked_levels": [1],   # Level đã mở
    "total_games":  0,
    "total_kills":  0,
}

_SAVE_FILE = os.path.join(SAVES_DIR, "save.json")
_MAX_HIGHSCORES = 5   # Giữ top 5 cao nhất mỗi màn


# ════════════════════════════════════════════════════════════════
#  HÀM TIỆN ÍCH
# ════════════════════════════════════════════════════════════════

def _ensure_dir():
    """Đảm bảo thư mục saves tồn tại."""
    os.makedirs(SAVES_DIR, exist_ok=True)


def load_save():
    """
    Tải dữ liệu từ file lưu.

    Trả về:
        dict: Dữ liệu game, hoặc default nếu file không tồn tại.
    """
    _ensure_dir()
    if not os.path.exists(_SAVE_FILE):
        return dict(_DEFAULT_SAVE)

    try:
        with open(_SAVE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Merge với default để xử lý các khóa mới
        merged = dict(_DEFAULT_SAVE)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, IOError):
        return dict(_DEFAULT_SAVE)


def _write_save(data):
    """Ghi dữ liệu xuống file."""
    _ensure_dir()
    try:
        with open(_SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


# ════════════════════════════════════════════════════════════════
#  ĐIỂM CAO (HIGHSCORE)
# ════════════════════════════════════════════════════════════════

def submit_score(level_id, score, wave_reached, victory=False):
    """
    Lưu điểm mới cho màn chơi.

    Tham số:
        level_id     (int)  : ID màn chơi (1/2/3).
        score        (int)  : Điểm đạt được.
        wave_reached (int)  : Wave đã đến.
        victory      (bool) : Có thắng không.

    Trả về:
        int: Thứ hạng mới (1=nhất), hoặc -1 nếu không lọt top.
    """
    import datetime
    data = load_save()
    key  = str(level_id)

    entry = {
        "score":   score,
        "wave":    wave_reached,
        "victory": victory,
        "date":    datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    scores = data["highscores"].get(key, [])
    scores.append(entry)
    # Sắp xếp giảm dần theo điểm
    scores.sort(key=lambda x: x["score"], reverse=True)
    # Giữ top N
    scores = scores[:_MAX_HIGHSCORES]
    data["highscores"][key] = scores

    # Mở khóa màn kế tiếp nếu thắng
    if victory:
        next_lv = level_id + 1
        unlocked = data.get("unlocked_levels", [1])
        if next_lv <= 3 and next_lv not in unlocked:
            unlocked.append(next_lv)
            data["unlocked_levels"] = unlocked

    # Thống kê
    data["total_games"] = data.get("total_games", 0) + 1

    _write_save(data)

    # Tính thứ hạng
    for rank, e in enumerate(scores, 1):
        if e is entry or (e["score"] == score and
                          e["date"] == entry["date"]):
            return rank
    return -1


def get_highscores(level_id):
    """
    Lấy bảng điểm cao của màn chơi.

    Trả về:
        list[dict]: Danh sách entry (sorted by score desc).
    """
    data = load_save()
    return data["highscores"].get(str(level_id), [])


def get_best_score(level_id):
    """
    Lấy điểm cao nhất của màn chơi.

    Trả về:
        int hoặc 0.
    """
    scores = get_highscores(level_id)
    if scores:
        return scores[0]["score"]
    return 0


def is_level_unlocked(level_id):
    """
    Kiểm tra màn chơi có bị khóa không.

    Trả về:
        bool.
    """
    data     = load_save()
    unlocked = data.get("unlocked_levels", [1])
    return level_id in unlocked


def unlock_level(level_id):
    """Mở khóa màn chơi theo ID."""
    data = load_save()
    if level_id not in data.get("unlocked_levels", [1]):
        data["unlocked_levels"].append(level_id)
        _write_save(data)


def get_stats():
    """
    Lấy thống kê toàn cục.

    Trả về:
        dict với total_games, total_kills, unlocked_levels.
    """
    data = load_save()
    return {
        "total_games":    data.get("total_games", 0),
        "total_kills":    data.get("total_kills", 0),
        "unlocked_levels": data.get("unlocked_levels", [1]),
    }


def update_kills(count):
    """Cộng thêm số quái tiêu diệt vào thống kê."""
    data = load_save()
    data["total_kills"] = data.get("total_kills", 0) + count
    _write_save(data)


def reset_saves():
    """Xóa toàn bộ dữ liệu lưu (dùng cho debug)."""
    if os.path.exists(_SAVE_FILE):
        os.remove(_SAVE_FILE)
