"""
tower.py - Các lớp tháp phòng thủ
Môn: IT003 - Cấu trúc dữ liệu và Giải thuật - UIT
"""

import pygame
import math
from settings import *


class Tower:
    """
    Lớp cơ sở (base class) cho tất cả các loại tháp.

    Thuộc tính chung:
        row, col    : Vị trí trên lưới.
        tower_type  : Loại tháp ('archer'/'cannon'/'mage').
        damage      : Sát thương mỗi viên đạn.
        range_cells : Tầm bắn tính bằng số ô.
        fire_rate   : Số lần bắn mỗi giây.
        target      : Enemy đang nhắm tới.
        cooldown    : Thời gian chờ còn lại giữa 2 lần bắn.
        shoot_flash : Timer cho hiệu ứng sáng khi bắn.
    """

    def __init__(self, row, col, tower_type):
        """
        Khởi tạo tháp.

        Tham số:
            row, col    (int): Vị trí ô trên lưới.
            tower_type  (str): Khóa trong TOWER_DATA.
        """
        self.row       = row
        self.col       = col
        self.tower_type = tower_type

        data = TOWER_DATA[tower_type]
        self.name          = data['name']
        self.damage        = data['damage']
        self.range_cells   = data['range']
        self.fire_rate     = data['fire_rate']
        self.cost          = data['cost']
        self.sell_value    = data['sell_value']
        self.color         = data['color']
        self.accent        = data['accent']
        self.bullet_color  = data['bullet_color']
        self.bullet_speed  = data['bullet_speed']
        self.bullet_size   = data['bullet_size']
        self.splash_radius = data['splash_radius']

        self.target       = None
        self.cooldown     = 0.0
        self.shoot_flash  = 0.0
        self.angle        = 0.0
        self.total_kills  = 0
        self.total_damage = 0

        self.px = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        self.py = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2


    def update(self, dt, enemies, projectiles):
        """
        Cập nhật logic tháp mỗi frame.

        Tham số:
            dt          (float): Delta time (giây).
            enemies     (list) : Danh sách enemy đang sống.
            projectiles (list) : Danh sách đạn (thêm vào đây khi bắn).
        """
        if self.cooldown > 0:
            self.cooldown -= dt
        if self.shoot_flash > 0:
            self.shoot_flash -= dt

        self.target = self._find_target(enemies)

        if self.target:
            tx, ty = self.target.px, self.target.py
            dx, dy = tx - self.px, ty - self.py
            self.angle = math.degrees(math.atan2(dy, dx))

            if self.cooldown <= 0:
                self._shoot(projectiles)
                self.cooldown = 1.0 / self.fire_rate

    def _find_target(self, enemies):
        """
        Tìm quái hợp lệ trong tầm để tấn công.
        Ưu tiên quái đi xa nhất trên đường (path_progress cao nhất).

        Trả về:
            Enemy hoặc None.
        """
        range_px = self.range_cells * CELL_SIZE
        best    = None
        best_progress = -1

        for enemy in enemies:
            if enemy.dead:
                continue
            dx = enemy.px - self.px
            dy = enemy.py - self.py
            dist = math.hypot(dx, dy)
            if dist <= range_px:
                if enemy.path_progress > best_progress:
                    best_progress = enemy.path_progress
                    best = enemy

        return best

    def _shoot(self, projectiles):
        """Tạo đạn và bắn về phía mục tiêu."""
        from projectile import Projectile
        proj = Projectile(
            start_x       = self.px,
            start_y       = self.py,
            target_enemy  = self.target,
            damage        = self.damage,
            speed         = self.bullet_speed * CELL_SIZE,
            color         = self.bullet_color,
            radius        = self.bullet_size,
            splash_radius = self.splash_radius * CELL_SIZE,
            tower_type    = self.tower_type,
        )
        projectiles.append(proj)
        self.shoot_flash = 0.12
        self.total_damage += self.damage


    def draw(self, surface):
        """Vẽ tháp lên surface."""
        self._draw_base(surface)
        self._draw_barrel(surface)
        self._draw_range_circle(surface)
        if self.shoot_flash > 0:
            self._draw_shoot_flash(surface)

    def _draw_base(self, surface):
        """Vẽ thân tháp – override ở subclass."""
        cx, cy = self.px, self.py
        pygame.draw.circle(surface, (15, 18, 28), (cx+3, cy+3), 22)
        pygame.draw.circle(surface, self.accent, (cx, cy), 24)
        pygame.draw.circle(surface, self.color,  (cx, cy), 20)
        pygame.draw.circle(surface, (min(self.color[0]+80, 255),
                                      min(self.color[1]+80, 255),
                                      min(self.color[2]+80, 255)),
                           (cx, cy), 20, 2)

    def _draw_barrel(self, surface):
        """Vẽ nòng súng quay theo góc nhắm."""
        cx, cy = self.px, self.py
        angle_rad = math.radians(self.angle)
        barrel_len = 20
        bx = cx + barrel_len * math.cos(angle_rad)
        by = cy + barrel_len * math.sin(angle_rad)
        pygame.draw.line(surface, self.accent,   (cx, cy), (bx, by), 6)
        pygame.draw.line(surface, self.color,    (cx, cy), (bx, by), 4)
        pygame.draw.circle(surface, self.color,  (cx, cy), 8)

    def _draw_range_circle(self, surface):
        """Vẽ vòng tầm bắn khi được chọn (mờ)."""
        if self.shoot_flash > 0 or self.target:
            range_px = int(self.range_cells * CELL_SIZE)
            alpha_surf = pygame.Surface((range_px*2, range_px*2), pygame.SRCALPHA)
            alpha = 25 if not self.shoot_flash else 60
            pygame.draw.circle(alpha_surf, (*self.color, alpha),
                               (range_px, range_px), range_px)
            pygame.draw.circle(alpha_surf, (*self.color, alpha+20),
                               (range_px, range_px), range_px, 1)
            surface.blit(alpha_surf, (self.px - range_px, self.py - range_px))

    def _draw_shoot_flash(self, surface):
        """Hiệu ứng sáng khi bắn."""
        r = int(12 * self.shoot_flash / 0.12)
        if r > 0:
            glow = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.bullet_color, 160),
                               (r*2, r*2), r*2)
            surface.blit(glow, (self.px - r*2, self.py - r*2))

    def draw_range(self, surface):
        """Vẽ vòng tầm bắn (khi hover/select trong panel)."""
        range_px = int(self.range_cells * CELL_SIZE)
        alpha_surf = pygame.Surface((range_px*2, range_px*2), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surf, (*self.color, 40),
                           (range_px, range_px), range_px)
        pygame.draw.circle(alpha_surf, (*self.color, 80),
                           (range_px, range_px), range_px, 2)
        surface.blit(alpha_surf, (self.px - range_px, self.py - range_px))


    def get_info(self):
        """Trả về dict thông tin tháp."""
        return {
            'name':     self.name,
            'damage':   self.damage,
            'range':    self.range_cells,
            'rate':     self.fire_rate,
            'sell':     self.sell_value,
            'kills':    self.total_kills,
        }



class ArcherTower(Tower):
    """
    Xạ Thủ – Tháp cung thủ.
    Bắn nhanh, đạn nhỏ, không AOE.
    Hình dạng: Tháp nhọn màu xanh lá với cung.
    """

    def __init__(self, row, col):
        super().__init__(row, col, 'archer')

    def _draw_base(self, surface):
        cx, cy = self.px, self.py

        pygame.draw.circle(surface, (15, 35, 20), (cx+3, cy+3), 22)

        pts = self._hexagon(cx, cy, 22)
        pygame.draw.polygon(surface, self.accent, pts)
        pts2 = self._hexagon(cx, cy, 18)
        pygame.draw.polygon(surface, self.color, pts2)

        pygame.draw.polygon(surface, (150, 255, 170), pts2, 2)

        pygame.draw.line(surface, (80, 50, 20), (cx-8, cy-8), (cx+8, cy+8), 2)
        pygame.draw.line(surface, (80, 50, 20), (cx-8, cy+8), (cx+8, cy-8), 2)

    def _hexagon(self, cx, cy, r):
        pts = []
        for i in range(6):
            a = math.radians(60 * i - 30)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return pts

    def _draw_barrel(self, surface):
        cx, cy = self.px, self.py
        angle_rad = math.radians(self.angle)
        length = 22
        bx = cx + length * math.cos(angle_rad)
        by = cy + length * math.sin(angle_rad)
        pygame.draw.line(surface, (140, 100, 40), (cx, cy), (bx, by), 3)
        tip_angle = angle_rad
        for da in [-0.4, 0.4]:
            ex = bx - 8 * math.cos(tip_angle + da)
            ey = by - 8 * math.sin(tip_angle + da)
            pygame.draw.line(surface, (200, 150, 50),
                             (int(bx), int(by)), (int(ex), int(ey)), 2)


class CannonTower(Tower):
    """
    Đại Bác – Tháp pháo.
    Bắn chậm, sát thương rất cao, có AOE nhỏ.
    Hình dạng: Khối vuông xám to với nòng pháo lớn.
    """

    def __init__(self, row, col):
        super().__init__(row, col, 'cannon')

    def _draw_base(self, surface):
        cx, cy = self.px, self.py

        pygame.draw.rect(surface, (20, 20, 28),
                         pygame.Rect(cx-20, cy-20, 43, 43), border_radius=6)

        body = pygame.Rect(cx-19, cy-19, 38, 38)
        pygame.draw.rect(surface, self.accent, body, border_radius=6)
        inner = pygame.Rect(cx-15, cy-15, 30, 30)
        pygame.draw.rect(surface, self.color, inner, border_radius=4)

        for dx, dy in [(-10,-10),(10,-10),(-10,10),(10,10)]:
            pygame.draw.circle(surface, self.accent, (cx+dx, cy+dy), 3)
            pygame.draw.circle(surface, (200, 200, 210), (cx+dx, cy+dy), 3, 1)

    def _draw_barrel(self, surface):
        cx, cy = self.px, self.py
        angle_rad = math.radians(self.angle)
        length = 26
        bx = cx + length * math.cos(angle_rad)
        by = cy + length * math.sin(angle_rad)
        pygame.draw.line(surface, self.accent, (cx, cy), (bx, by), 10)
        pygame.draw.line(surface, self.color,  (cx, cy), (bx, by), 7)
        pygame.draw.circle(surface, (100, 100, 115),
                           (int(bx), int(by)), 5)
        pygame.draw.circle(surface, self.accent, (cx, cy), 10)
        pygame.draw.circle(surface, self.color,  (cx, cy), 7)


class MageTower(Tower):
    """
    Pháp Sư – Tháp phép thuật.
    Tầm bắn xa nhất, hiệu ứng đẹp.
    Hình dạng: Tháp nhọn tím với quả cầu phép thuật.
    """

    def __init__(self, row, col):
        super().__init__(row, col, 'mage')
        self._orb_pulse = 0.0

    def update(self, dt, enemies, projectiles):
        self._orb_pulse = (self._orb_pulse + dt * 3) % (2 * math.pi)
        super().update(dt, enemies, projectiles)

    def _draw_base(self, surface):
        cx, cy = self.px, self.py

        pts = self._diamond(cx, cy, 24)
        pygame.draw.polygon(surface, (20, 10, 35), [(p[0]+3, p[1]+3) for p in pts])

        pygame.draw.polygon(surface, self.accent, self._diamond(cx, cy, 23))
        pygame.draw.polygon(surface, self.color,  self._diamond(cx, cy, 19))

        pulse = abs(math.sin(self._orb_pulse))
        glow_c = (int(180 + 75*pulse), int(80 + 50*pulse), 255)
        pygame.draw.polygon(surface, glow_c, self._diamond(cx, cy, 19), 2)

        orb_r = int(7 + 2 * pulse)
        orb_surf = pygame.Surface((orb_r*4, orb_r*4), pygame.SRCALPHA)
        pygame.draw.circle(orb_surf, (200, 120, 255, 60),
                           (orb_r*2, orb_r*2), orb_r*2)
        surface.blit(orb_surf, (cx - orb_r*2, cy - orb_r*2))
        pygame.draw.circle(surface, (220, 150, 255), (cx, cy), orb_r)
        pygame.draw.circle(surface, (255, 200, 255), (cx, cy), orb_r, 1)

    def _diamond(self, cx, cy, r):
        return [
            (cx,   cy-r),
            (cx+r, cy),
            (cx,   cy+r),
            (cx-r, cy),
        ]

    def _draw_barrel(self, surface):
        cx, cy = self.px, self.py
        angle_rad = math.radians(self.angle)
        length = 20
        bx = cx + length * math.cos(angle_rad)
        by = cy + length * math.sin(angle_rad)

        pulse = abs(math.sin(self._orb_pulse))
        glow_c = (int(160 + 60*pulse), int(80 + 40*pulse), 255)

        for i in range(3):
            a = angle_rad + 0.3 * (i - 1)
            ex = cx + (length * 0.6) * math.cos(a)
            ey = cy + (length * 0.6) * math.sin(a)
            pygame.draw.line(surface, glow_c,
                             (cx, cy), (int(ex), int(ey)), 2)
        pygame.draw.line(surface, (220, 150, 255), (cx, cy), (bx, by), 3)



def create_tower(tower_type, row, col):
    """
    Factory function tạo tháp theo loại.

    Tham số:
        tower_type (str): 'archer' / 'cannon' / 'mage'
        row, col   (int): Vị trí trên lưới.

    Trả về:
        Tower instance.
    """
    _map = {
        'archer': ArcherTower,
        'cannon': CannonTower,
        'mage':   MageTower,
    }
    cls = _map.get(tower_type)
    if cls is None:
        raise ValueError(f"Loại tháp không hợp lệ: {tower_type}")
    return cls(row, col)


def draw_tower_preview(surface, tower_type, cx, cy, scale=1.0):
    """
    Vẽ preview tháp tại tọa độ pixel (cx, cy) – dùng trong panel.

    Tham số:
        surface   (pygame.Surface): Đích vẽ.
        tower_type (str)          : Loại tháp.
        cx, cy    (int)           : Tâm vẽ.
        scale     (float)         : Tỉ lệ. (reserved)
    """
    data   = TOWER_DATA[tower_type]
    color  = data['color']
    accent = data['accent']

    if tower_type == 'archer':
        pts = _hexagon_pts(cx, cy, 18)
        pygame.draw.polygon(surface, accent, pts)
        pts2 = _hexagon_pts(cx, cy, 14)
        pygame.draw.polygon(surface, color, pts2)
        pygame.draw.polygon(surface, (150, 255, 170), pts2, 2)

    elif tower_type == 'cannon':
        body = pygame.Rect(cx-15, cy-15, 30, 30)
        pygame.draw.rect(surface, accent, body, border_radius=5)
        inner = pygame.Rect(cx-11, cy-11, 22, 22)
        pygame.draw.rect(surface, color, inner, border_radius=3)
        pygame.draw.rect(surface, (200, 200, 210), inner, 2, border_radius=3)

    elif tower_type == 'mage':
        pts = [(cx, cy-20), (cx+20, cy), (cx, cy+20), (cx-20, cy)]
        pygame.draw.polygon(surface, accent, pts)
        pts2 = [(cx, cy-16), (cx+16, cy), (cx, cy+16), (cx-16, cy)]
        pygame.draw.polygon(surface, color, pts2)
        pygame.draw.circle(surface, (220, 150, 255), (cx, cy), 6)


def _hexagon_pts(cx, cy, r):
    pts = []
    for i in range(6):
        a = math.radians(60 * i - 30)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts
