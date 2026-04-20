"""
enemy.py - Các lớp quái vật
Môn: IT003 - Cấu trúc dữ liệu và Giải thuật - UIT

Quái di chuyển theo đường BFS được tính bởi grid.
Khi đường bị thay đổi (tháp mới xây), path được cập nhật động.
"""

import pygame
import math
import font_manager
from settings import *


class Enemy:
    """
    Lớp cơ sở cho tất cả quái vật.

    Quái di chuyển từng bước theo danh sách tọa độ ô (path)
    do BFS tính toán. Khi path thay đổi, quái tự cập nhật
    từ vị trí hiện tại của mình.

    Thuộc tính quan trọng:
        path          – Danh sách (row, col) tạo thành đường đi.
        path_idx      – Chỉ số ô tiếp theo trong path.
        path_progress – Số bước đã đi (dùng để xác định mục tiêu ưu tiên).
        px, py        – Vị trí pixel hiện tại (float, để di chuyển mượt).
        hp            – Máu hiện tại.
        dead          – True nếu đã chết (bị tiêu diệt hoặc đến base).
        reached_base  – True nếu đã đến căn cứ.
    """

    def __init__(self, enemy_type, path, wave_scale=1.0):
        """
        Khởi tạo quái.

        Tham số:
            enemy_type  (str)  : Khóa trong ENEMY_DATA.
            path        (list) : Danh sách (row,col) từ BFS.
            wave_scale  (float): Hệ số tăng sức mạnh theo wave.
        """
        self.enemy_type = enemy_type
        data = ENEMY_DATA[enemy_type]

        self.name    = data['name']
        self.max_hp  = int(data['hp'] * wave_scale)
        self.hp      = self.max_hp
        self.speed   = data['speed'] * CELL_SIZE
        self.reward  = data['reward']
        self.base_damage = data['damage']
        self.color   = data['color']
        self.outline = data['outline']
        self.size    = data['size']

        self.path      = list(path)
        self.path_idx  = 1
        self.path_progress = 0.0

        if path:
            r, c = path[0]
            self.px = float(GRID_OFFSET_X + c * CELL_SIZE + CELL_SIZE // 2)
            self.py = float(GRID_OFFSET_Y + r * CELL_SIZE + CELL_SIZE // 2)
        else:
            self.px = self.py = 0.0

        self.dead         = False
        self.reached_base = False

        self.hit_flash     = 0.0
        self.death_timer   = 0.0

        self.direction = (1, 0)


    def update_path(self, new_path):
        """
        Cập nhật đường đi mới khi grid bị thay đổi.

        Quái cần tìm ô gần nhất trong new_path so với vị trí hiện tại,
        rồi tiếp tục từ đó.

        Tham số:
            new_path (list[tuple]): Đường đi mới từ BFS.
        """
        if not new_path:
            return

        best_idx  = 0
        best_dist = float('inf')
        for i, (r, c) in enumerate(new_path):
            cx = GRID_OFFSET_X + c * CELL_SIZE + CELL_SIZE // 2
            cy = GRID_OFFSET_Y + r * CELL_SIZE + CELL_SIZE // 2
            d  = math.hypot(cx - self.px, cy - self.py)
            if d < best_dist:
                best_dist = d
                best_idx  = i

        self.path     = list(new_path)
        self.path_idx = min(best_idx + 1, len(new_path) - 1)
        self.path_progress = float(best_idx)

    def update_path_from_current(self, grid):
        """
        Tính lại đường đi mới từ vị trí hiện tại của quái tới đích (nhờ hàm get_random_path(start)).
        Tránh trường hợp bị giật lùi về điểm gần nhất trên một route hoàn toàn khác.
        """
        r = int((self.py - GRID_OFFSET_Y) / CELL_SIZE)
        c = int((self.px - GRID_OFFSET_X) / CELL_SIZE)
        r = max(0, min(r, grid.rows - 1))
        c = max(0, min(c, grid.cols - 1))

        new_path = grid.get_random_path(start=(r, c))
        if new_path:
            self.path = new_path
            self.path_idx = 1 if len(new_path) > 1 else 0
            self.path_progress = 0.0


    def update(self, dt):
        """
        Cập nhật vị trí quái mỗi frame.

        Quái di chuyển theo từng điểm trong path cho đến khi
        đến ô BASE, lúc đó đánh dấu reached_base = True.

        Tham số:
            dt (float): Delta time (giây).
        """
        if self.dead:
            return

        if self.hit_flash > 0:
            self.hit_flash -= dt

        if self.path_idx >= len(self.path):
            self.reached_base = True
            self.dead         = True
            return

        target_r, target_c = self.path[self.path_idx]
        target_x = GRID_OFFSET_X + target_c * CELL_SIZE + CELL_SIZE // 2
        target_y = GRID_OFFSET_Y + target_r * CELL_SIZE + CELL_SIZE // 2

        dx = target_x - self.px
        dy = target_y - self.py
        dist = math.hypot(dx, dy)

        move_dist = self.speed * dt

        if dist <= move_dist:
            self.px = float(target_x)
            self.py = float(target_y)
            self.path_progress = float(self.path_idx)
            self.path_idx += 1
        else:
            self.px += dx / dist * move_dist
            self.py += dy / dist * move_dist
            if dist > 0:
                self.direction = (dx / dist, dy / dist)
            frac = 1.0 - dist / (self.speed / max(dt, 0.001))
            self.path_progress = float(self.path_idx - 1) + min(frac, 1.0)


    def take_damage(self, amount, shooter=None):
        """
        Quái nhận sát thương.

        Tham số:
            amount  (int/float): Lượng sát thương.
            shooter (Tower)    : Tháp gây sát thương (để tính kills).

        Trả về:
            bool: True nếu quái chết sau đòn này.
        """
        if self.dead:
            return False
        self.hp -= amount
        self.hit_flash = 0.15

        if self.hp <= 0:
            self.hp   = 0
            self.dead = True
            if shooter:
                shooter.total_kills += 1
            return True
        return False


    def draw(self, surface):
        """Vẽ quái và thanh HP lên surface."""
        if self.dead:
            return
        cx, cy = int(self.px), int(self.py)

        shadow = pygame.Surface((self.size*3, self.size), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 80),
                            (0, 0, self.size*3, self.size))
        surface.blit(shadow, (cx - self.size*3//2, cy + self.size - 4))

        self._draw_body(surface, cx, cy)

        self._draw_hp_bar(surface, cx, cy)

        if self.hit_flash > 0:
            a = int(200 * self.hit_flash / 0.15)
            flash = pygame.Surface((self.size*2+4, self.size*2+4), pygame.SRCALPHA)
            pygame.draw.circle(flash, (255, 80, 80, a),
                               (self.size+2, self.size+2), self.size+2)
            surface.blit(flash, (cx - self.size - 2, cy - self.size - 2))

    def _draw_body(self, surface, cx, cy):
        """Vẽ thân quái – override ở subclass."""
        s = self.size
        pygame.draw.circle(surface, self.outline, (cx, cy), s + 2)
        pygame.draw.circle(surface, self.color, (cx, cy), s)
        hl = (min(self.color[0]+80, 255),
              min(self.color[1]+80, 255),
              min(self.color[2]+80, 255))
        pygame.draw.circle(surface, hl, (cx - s//3, cy - s//3), s//4)

    def _draw_hp_bar(self, surface, cx, cy):
        """Vẽ thanh máu phía trên đầu quái."""
        bar_w = self.size * 2 + 4
        bar_h = 5
        bx    = cx - bar_w // 2
        by    = cy - self.size - 10

        pygame.draw.rect(surface, (20, 20, 20),
                         pygame.Rect(bx-1, by-1, bar_w+2, bar_h+2),
                         border_radius=2)
        ratio = self.hp / self.max_hp
        fill_w = int(bar_w * ratio)
        if ratio > 0.6:
            clr = C_HP_FULL
        elif ratio > 0.3:
            clr = C_HP_MED
        else:
            clr = C_HP_LOW
        if fill_w > 0:
            pygame.draw.rect(surface, clr,
                             pygame.Rect(bx, by, fill_w, bar_h),
                             border_radius=2)



class Goblin(Enemy):
    """Quỷ Lùn – Nhỏ, nhanh, dễ hạ."""

    def __init__(self, path, wave_scale=1.0):
        super().__init__('goblin', path, wave_scale)

    def _draw_body(self, surface, cx, cy):
        s = self.size
        pygame.draw.circle(surface, self.outline, (cx, cy), s + 2)
        pygame.draw.circle(surface, self.color, (cx, cy), s)
        ear_pts = [
            [(cx-s-2, cy-s//2), (cx-s+4, cy-s*2), (cx-s+8, cy-s//2)],
            [(cx+s+2, cy-s//2), (cx+s-4, cy-s*2), (cx+s-8, cy-s//2)],
        ]
        for ep in ear_pts:
            pygame.draw.polygon(surface, self.outline, ep)
            inner = [(ep[0][0]+2, ep[0][1]+2),
                     (ep[1][0],   ep[1][1]+4),
                     (ep[2][0]-2, ep[2][1]+2)]
            pygame.draw.polygon(surface, self.color, inner)
        pygame.draw.circle(surface, (255, 60, 60), (cx-4, cy-3), 3)
        pygame.draw.circle(surface, (255, 60, 60), (cx+4, cy-3), 3)
        pygame.draw.circle(surface, (20, 20, 20),  (cx-3, cy-3), 1)
        pygame.draw.circle(surface, (20, 20, 20),  (cx+5, cy-3), 1)


class Orc(Enemy):
    """Orc Chiến Binh – Trung bình, bền hơn."""

    def __init__(self, path, wave_scale=1.0):
        super().__init__('orc', path, wave_scale)

    def _draw_body(self, surface, cx, cy):
        s = self.size
        pygame.draw.circle(surface, self.outline, (cx, cy), s + 2)
        pygame.draw.circle(surface, self.color, (cx, cy), s)
        horn_pts = [
            [(cx-6, cy-s+2), (cx-8, cy-s-8), (cx-3, cy-s+2)],
            [(cx+6, cy-s+2), (cx+8, cy-s-8), (cx+3, cy-s+2)],
        ]
        for hp_ in horn_pts:
            pygame.draw.polygon(surface, (150, 100, 50), hp_)
        pygame.draw.circle(surface, (255, 200, 60), (cx-5, cy-3), 4)
        pygame.draw.circle(surface, (255, 200, 60), (cx+5, cy-3), 4)
        pygame.draw.circle(surface, (30, 10, 10), (cx-4, cy-3), 2)
        pygame.draw.circle(surface, (30, 10, 10), (cx+6, cy-3), 2)
        pygame.draw.line(surface, (230, 220, 180),
                         (cx-4, cy+4), (cx-6, cy+9), 3)
        pygame.draw.line(surface, (230, 220, 180),
                         (cx+4, cy+4), (cx+6, cy+9), 3)


class Troll(Enemy):
    """Quái Khổng Lồ – Chậm, cực bền, gây nhiều sát thương."""

    def __init__(self, path, wave_scale=1.0):
        super().__init__('troll', path, wave_scale)
        self._walk_anim = 0.0

    def update(self, dt):
        self._walk_anim += dt * 4
        super().update(dt)

    def _draw_body(self, surface, cx, cy):
        s = self.size
        shadow = pygame.Surface((s*4, s*2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,100), (0,0,s*4,s*2))
        surface.blit(shadow, (cx - s*2, cy + s - 6))

        pygame.draw.circle(surface, self.outline, (cx, cy), s + 4)
        pygame.draw.circle(surface, self.color, (cx, cy), s + 2)
        for dx, dy in [(-10,-8),(0,-12),(10,-8),(-14,0),(14,0)]:
            pygame.draw.circle(surface, self.outline, (cx+dx, cy+dy), 4)

        eye_clr = (255, 80, 20)
        pygame.draw.circle(surface, eye_clr, (cx-7, cy-6), 5)
        pygame.draw.circle(surface, eye_clr, (cx+7, cy-6), 5)
        pygame.draw.circle(surface, (255, 200, 80), (cx-6, cy-6), 2)
        pygame.draw.circle(surface, (255, 200, 80), (cx+8, cy-6), 2)

        font = font_manager.get(max(s-6, 9), bold=True)
        lbl  = font.render("T", True, (220, 240, 255))
        surface.blit(lbl, lbl.get_rect(center=(cx, cy+4)))



def create_enemy(enemy_type, path, wave_scale=1.0):
    """
    Factory function tạo enemy theo loại.

    Tham số:
        enemy_type  (str)  : 'goblin' / 'orc' / 'troll'
        path        (list) : Danh sách (row,col) từ BFS.
        wave_scale  (float): Hệ số nhân HP theo wave (mặc định 1.0).

    Trả về:
        Enemy instance.
    """
    _map = {
        'goblin': Goblin,
        'orc':    Orc,
        'troll':  Troll,
    }
    cls = _map.get(enemy_type)
    if cls is None:
        raise ValueError(f"Loại quái không hợp lệ: {enemy_type}")
    return cls(path, wave_scale)
