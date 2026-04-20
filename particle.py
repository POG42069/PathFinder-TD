"""
particle.py - Hệ thống hiệu ứng hạt (particles)
Môn: IT003 - Cấu trúc dữ liệu và Giải thuật - UIT
"""

import pygame
import random
import math
import font_manager


class Particle:
    """
    Hạt đơn lẻ cho hiệu ứng hình ảnh (nổ, đánh, etc.).
    Mỗi particle có vị trí, vận tốc, màu sắc và lifetime.
    """

    def __init__(self, x, y, vx, vy, color, lifetime, radius=3,
                 gravity=0.0, alpha_fade=True):
        self.x        = float(x)
        self.y        = float(y)
        self.vx       = float(vx)
        self.vy       = float(vy)
        self.color    = color
        self.lifetime = lifetime    # giây tổng
        self.age      = 0.0         # giây đã sống
        self.radius   = radius
        self.gravity  = gravity     # pixels/s^2 xuống dưới
        self.alpha_fade = alpha_fade
        self.dead     = False

    def update(self, dt):
        if self.dead:
            return
        self.age += dt
        if self.age >= self.lifetime:
            self.dead = True
            return
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.vy += self.gravity * dt
        # Ma sát nhẹ
        self.vx *= 0.97
        self.vy *= 0.97

    def draw(self, surface):
        if self.dead:
            return
        ratio   = 1.0 - self.age / self.lifetime
        r_cur   = max(int(self.radius * ratio), 1)
        alpha   = int(255 * ratio) if self.alpha_fade else 255

        surf = pygame.Surface((r_cur*2+2, r_cur*2+2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha),
                           (r_cur+1, r_cur+1), r_cur)
        surface.blit(surf, (int(self.x) - r_cur - 1,
                             int(self.y) - r_cur - 1))


class SparkParticle(Particle):
    """Hạt tia sáng (tia lửa dẹt)."""

    def draw(self, surface):
        if self.dead:
            return
        ratio = 1.0 - self.age / self.lifetime
        alpha = int(255 * ratio)
        ex = self.x + self.vx * 0.05
        ey = self.y + self.vy * 0.05
        surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        clr = (*self.color, alpha)
        pygame.draw.line(surf, clr,
                         (50, 50),
                         (int(50 + ex - self.x), int(50 + ey - self.y)),
                         max(1, int(self.radius * ratio)))
        surface.blit(surf, (int(self.x) - 50, int(self.y) - 50))


class TextParticle:
    """Hiển thị số sát thương / điểm nhảy lên."""

    def __init__(self, x, y, text, color=(255, 230, 50),
                 font_size=18, lifetime=1.2):
        self.x        = float(x)
        self.y        = float(y)
        self.text     = text
        self.color    = color
        self.font     = font_manager.get(font_size, bold=True)
        self.lifetime = lifetime
        self.age      = 0.0
        self.dead     = False
        self.vy       = -60.0   # byte lên trên

    def update(self, dt):
        if self.dead:
            return
        self.age += dt
        if self.age >= self.lifetime:
            self.dead = True
            return
        self.y  += self.vy * dt
        self.vy *= 0.95   # giảm dần

    def draw(self, surface):
        if self.dead:
            return
        ratio = 1.0 - self.age / self.lifetime
        alpha = int(255 * ratio)
        txt_surf = self.font.render(self.text, True, self.color)
        txt_surf.set_alpha(alpha)
        surface.blit(txt_surf, (int(self.x) - txt_surf.get_width()//2,
                                  int(self.y) - txt_surf.get_height()//2))


# ════════════════════════════════════════════════════════════════
#  HÀM SPAWN CÁC HIỆU ỨNG
# ════════════════════════════════════════════════════════════════

def spawn_hit_particles(particles, x, y, color, count=6):
    """Tạo tia sáng nhỏ khi đạn chạm quái."""
    for _ in range(count):
        angle  = random.uniform(0, math.pi * 2)
        speed  = random.uniform(40, 120)
        vx     = speed * math.cos(angle)
        vy     = speed * math.sin(angle)
        r      = random.randint(2, 5)
        life   = random.uniform(0.15, 0.35)
        particles.append(Particle(x, y, vx, vy, color, life, r,
                                   gravity=80))


def spawn_explosion_particles(particles, x, y, color, count=18):
    """Tạo vụ nổ phong phú khi quái chết."""
    # Mảnh tung ra
    for _ in range(count):
        angle  = random.uniform(0, math.pi * 2)
        speed  = random.uniform(60, 200)
        vx     = speed * math.cos(angle)
        vy     = speed * math.sin(angle)
        r      = random.randint(3, 8)
        life   = random.uniform(0.4, 0.9)
        clr    = (
            min(color[0] + random.randint(-40, 60), 255),
            min(color[1] + random.randint(-40, 60), 255),
            min(color[2] + random.randint(-40, 60), 255),
        )
        particles.append(Particle(x, y, vx, vy, clr, life, r,
                                   gravity=120))

    # Tia sáng
    for _ in range(6):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(100, 250)
        vx    = speed * math.cos(angle)
        vy    = speed * math.sin(angle)
        particles.append(SparkParticle(x, y, vx, vy,
                                        (255, 230, 100),
                                        random.uniform(0.2, 0.5), 2))


def spawn_gold_text(particles, x, y, amount):
    """Hiển thị số vàng nhận được."""
    particles.append(TextParticle(x, y, f"+{amount}g",
                                   color=(255, 210, 40),
                                   font_size=16))


def spawn_damage_text(particles, x, y, damage):
    """Hiển thị số sát thương."""
    particles.append(TextParticle(x, y - 20, f"-{damage}",
                                   color=(255, 80, 80),
                                   font_size=14))


def spawn_base_hit_particles(particles, x, y):
    """Hiệu ứng khi quái chạm base."""
    for _ in range(20):
        angle  = random.uniform(0, math.pi * 2)
        speed  = random.uniform(80, 220)
        vx     = speed * math.cos(angle)
        vy     = speed * math.sin(angle)
        clr    = random.choice([(255, 60, 60), (255, 120, 60),
                                  (255, 200, 80)])
        life   = random.uniform(0.5, 1.2)
        particles.append(Particle(x, y, vx, vy, clr, life,
                                   random.randint(4, 10), gravity=100))
    particles.append(TextParticle(x, y - 30, "DAMAGE!",
                                   color=(255, 80, 80), font_size=20,
                                   lifetime=1.5))


def update_particles(particles, dt):
    """Cập nhật tất cả particles và xóa cái đã chết."""
    for p in particles:
        p.update(dt)
    # Xóa dead particles
    particles[:] = [p for p in particles if not p.dead]


def draw_particles(particles, surface):
    """Vẽ tất cả particles."""
    for p in particles:
        p.draw(surface)
