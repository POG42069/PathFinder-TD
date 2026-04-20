"""
wave.py - Quản lý hệ thống wave (đợt quái)
Môn: IT003 - Cấu trúc dữ liệu và Giải thuật - UIT
"""

import pygame
from settings import *
from enemy import create_enemy


class WaveManager:
    """
    Quản lý việc spawn quái theo từng wave.

    Wave Manager đọc WAVE_DEFINITIONS từ settings,
    điều phối thời điểm spawn từng quái, và theo dõi
    trạng thái hoàn thành của mỗi wave.

    Thuộc tính:
        wave_idx        – Chỉ số wave hiện tại (0-based).
        state           – Trạng thái: 'idle'/'spawning'/'waiting'/'done'
        enemies         – Danh sách enemy đang sống trên bản đồ.
        pending         – Hàng đợi các quái chưa spawn: [(enemy_type, delay)]
        spawn_timer     – Thời gian chờ trước khi spawn quái tiếp theo.
        break_timer     – Đếm ngược giữa các wave.
    """

    def __init__(self):
        self.wave_idx    = 0           # Wave hiện tại (0-based)
        self.state       = 'idle'      # idle → spawning → waiting → idle...
        self.enemies     = []          # Enemy đang sống
        self.pending     = []          # Queue spawn: [(type, cumulative_time)]
        self.spawn_timer = 0.0         # Thời gian chờ đến quái tiếp theo
        self.break_timer = 0.0         # Thời gian nghỉ giữa wave

        # Thống kê
        self.total_spawned  = 0
        self.total_killed   = 0

    # ════════════════════════════════════════════════════════════
    #  ĐIỀU KHIỂN WAVE
    # ════════════════════════════════════════════════════════════

    @property
    def current_wave(self):
        """Wave hiện tại (1-based để hiển thị)."""
        return self.wave_idx + 1

    @property
    def is_done(self):
        """Đã hoàn thành tất cả waves chưa?"""
        return self.wave_idx >= TOTAL_WAVES

    @property
    def all_enemies_dead(self):
        """Tất cả quái trên bản đồ đã bị hạ/đến base chưa?"""
        return all(e.dead for e in self.enemies)

    def start_next_wave(self, grid):
        """
        Bắt đầu wave tiếp theo – spawn quái từ WAVE_DEFINITIONS.

        Tham số:
            grid (Grid): Dùng để lấy path hiện tại cho quái.
        """
        if self.is_done:
            return False

        wave_def  = WAVE_DEFINITIONS[self.wave_idx]
        path      = grid.get_path()

        # Tính hệ số scale HP theo wave
        scale = 1.0 + self.wave_idx * 0.15

        # Xây dựng hàng đợi spawn
        self.pending.clear()
        for enemy_type, count, delay in wave_def:
            for i in range(count):
                self.pending.append((enemy_type, delay, scale))

        self.spawn_timer = 0.5   # Dừng 0.5s trước khi bắt đầu spawn đợt này
        self.state       = 'spawning'
        self._current_path = list(path)
        return True

    def can_start_wave(self):
        """Có thể bắt đầu wave tiếp theo không?"""
        return (self.state == 'idle' and
                not self.is_done and
                self.all_enemies_dead)

    # ════════════════════════════════════════════════════════════
    #  UPDATE
    # ════════════════════════════════════════════════════════════

    def update(self, dt, grid, on_wave_complete=None):
        """
        Cập nhật WaveManager mỗi frame.

        Tham số:
            dt               (float): Delta time.
            grid             (Grid) : Để lấy path BFS mới nhất.
            on_wave_complete (func) : Callback khi wave hoàn thành.
        """
        # Cập nhật tất cả enemy đang sống
        dead_indices = []

        for i, enemy in enumerate(self.enemies):
            enemy.update(dt)

        # Xóa enemy đã chết khỏi danh sách
        self.enemies = [e for e in self.enemies if not e.dead]

        # ── State machine ──
        if self.state == 'spawning':
            self._handle_spawning(dt, grid)

        elif self.state == 'waiting':
            # Chờ tất cả quái bị hạ
            if self.all_enemies_dead:
                self.wave_idx += 1
                if self.is_done:
                    self.state = 'done'
                else:
                    self.break_timer = WAVE_BREAK_TIME
                    self.state       = 'break'
                if on_wave_complete:
                    on_wave_complete(self.wave_idx)

        elif self.state == 'break':
            self.break_timer -= dt
            if self.break_timer <= 0:
                self.state = 'idle'

    def _handle_spawning(self, dt, grid):
        """Xử lý spawn quái từ hàng đợi pending."""
        self.spawn_timer -= dt

        if self.spawn_timer <= 0 and self.pending:
            enemy_type, delay, scale = self.pending.pop(0)

            # Tạo enemy với đường BFS ngẫu nhiên (mỗi con 1 đường ngắn nhất khác nhau)
            enemy = create_enemy(enemy_type, grid.get_random_path(), scale)
            self.enemies.append(enemy)
            self.total_spawned += 1

            # Đặt timer cho quái tiếp theo
            if self.pending:
                self.spawn_timer = delay
            else:
                # Hết quái cần spawn, chuyển sang waiting
                self.state = 'waiting'

    # ════════════════════════════════════════════════════════════
    #  THÔNG TIN
    # ════════════════════════════════════════════════════════════

    def get_enemies_remaining(self):
        """Số quái còn lại (sống + chưa spawn)."""
        alive = sum(1 for e in self.enemies if not e.dead)
        return alive + len(self.pending)

    def get_progress_text(self):
        """Chuỗi hiển thị tiến trình wave."""
        if self.is_done:
            return "Hoàn thành!"
        if self.state == 'idle':
            return f"Wave {self.current_wave}/{TOTAL_WAVES} - Sẵn sàng"
        if self.state == 'break':
            return f"Wave tiếp theo: {self.break_timer:.1f}s"
        if self.state in ('spawning', 'waiting'):
            return f"Wave {self.wave_idx+1}/{TOTAL_WAVES} - Đang tấn công"
        return ""

    def get_break_timer(self):
        """Thời gian còn lại giữa wave."""
        return max(self.break_timer, 0.0)
