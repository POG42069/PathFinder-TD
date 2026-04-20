"""
projectile.py - Hệ thống đạn bắn
Môn: IT003 - Cấu trúc dữ liệu và Giải thuật - UIT
"""

import pygame
import math
from settings import *


class Projectile:
    """
    Đạn bay từ tháp đến quái.

    Đạn di chuyển về phía enemy mục tiêu. Nếu enemy chết trước khi
    đạn đến nơi, đạn tự hủy. Khi chạm, gây sát thương (và AOE nếu có).
    """

    def __init__(self, start_x, start_y, target_enemy, damage,
                 speed, color, radius, splash_radius=0, tower_type='archer'):
        """
        Tham số:
            start_x, start_y (float): Tọa độ xuất phát (pixel).
            target_enemy (Enemy)    : Quái mục tiêu.
            damage (int)            : Sát thương trực tiếp.
            speed (float)           : Tốc độ bay (pixel/giây).
            color (tuple)           : Màu đạn.
            radius (int)            : Bán kính đạn (vẽ).
            splash_radius (float)   : Bán kính AOE (pixel), 0 nếu không có.
            tower_type (str)        : Loại tháp bắn.
        """
        self.x      = float(start_x)
        self.y      = float(start_y)
        self.target = target_enemy
        self.damage = damage
        self.speed  = speed
        self.color  = color
        self.radius = radius
        self.splash = splash_radius
        self.tower_type = tower_type

        self.dead    = False
        self.hit     = False

        self.trail: list[tuple] = []
        self.max_trail = 8

        self.lifetime = 4.0


    def update(self, dt, enemies, particles_list, gold_callback, kill_callback):
        """
        Cập nhật vị trí đạn mỗi frame.

        Tham số:
            dt              (float): Delta time.
            enemies         (list) : Để tính AOE.
            particles_list  (list) : Thêm particles khi nổ.
            gold_callback   (func) : Gọi khi giết quái để thêm vàng.
            kill_callback   (func) : Gọi khi giết quái để tính điểm.
        """
        if self.dead:
            return

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.dead = True
            return

        if self.target.dead:
            self.dead = True
            return

        tx, ty = self.target.px, self.target.py
        dx, dy = tx - self.x, ty - self.y
        dist   = math.hypot(dx, dy)

        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

        move = self.speed * dt
        if dist <= move + self.radius:
            self.x = tx
            self.y = ty
            self._on_hit(enemies, particles_list, gold_callback, kill_callback)
        else:
            self.x += dx / dist * move
            self.y += dy / dist * move

    def _on_hit(self, enemies, particles_list, gold_callback, kill_callback):
        """Xử lý khi đạn chạm mục tiêu."""
        from particle import spawn_hit_particles, spawn_explosion_particles

        killed = self.target.take_damage(self.damage)
        spawn_hit_particles(particles_list, int(self.x), int(self.y),
                            self.color)

        if killed:
            spawn_explosion_particles(particles_list,
                                      int(self.target.px),
                                      int(self.target.py),
                                      self.target.color)
            gold_callback(self.target.reward)
            kill_callback()

        if self.splash > 0:
            for e in enemies:
                if e is self.target or e.dead:
                    continue
                d = math.hypot(e.px - self.x, e.py - self.y)
                if d <= self.splash:
                    ratio  = 1.0 - d / self.splash
                    aoe_dmg = int(self.damage * ratio * 0.6)
                    if aoe_dmg > 0:
                        e_killed = e.take_damage(aoe_dmg)
                        if e_killed:
                            spawn_explosion_particles(
                                particles_list,
                                int(e.px), int(e.py), e.color)
                            gold_callback(e.reward)
                            kill_callback()

        self.dead = True


    def draw(self, surface):
        """Vẽ đạn và vết bay."""
        if self.dead:
            return

        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(180 * i / max(len(self.trail), 1))
            r     = max(self.radius - (len(self.trail)-i), 1)
            trail_surf = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*self.color, alpha),
                               (r+1, r+1), r)
            surface.blit(trail_surf, (tx - r - 1, ty - r - 1))

        cx, cy = int(self.x), int(self.y)

        glow_r = self.radius + 4
        glow   = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 80), (glow_r, glow_r), glow_r)
        surface.blit(glow, (cx - glow_r, cy - glow_r))

        pygame.draw.circle(surface, (255, 255, 255),
                           (cx, cy), self.radius + 1)
        pygame.draw.circle(surface, self.color, (cx, cy), self.radius)
