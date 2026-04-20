"""
ui.py - Hệ thống giao diện người dùng
Môn: IT003 - Cấu trúc dữ liệu và Giải thuật - UIT

Các màn hình:
    MenuScreen        – Màn hình chính
    LevelSelectScreen – Chọn màn chơi
    HUD               – Thanh thông tin trong game
    TowerPanel        – Panel bên phải chọn tháp
    PauseOverlay      – Màn hình tạm dừng
    GameOverScreen    – Thua
    VictoryScreen     – Thắng
    HighscoreScreen   – Bảng điểm
"""

import pygame
import math
import random
import font_manager
from settings import *
from tower import draw_tower_preview


# ════════════════════════════════════════════════════════════════
#  LỚP BUTTON CƠ BẢN
# ════════════════════════════════════════════════════════════════

class Button:
    """Nút bấm có hover và click animation."""

    def __init__(self, rect, text, color=None, text_color=C_WHITE,
                 font_size=18, border_radius=10, icon=None):
        self.rect          = pygame.Rect(rect)
        self.text          = text
        self.base_color    = color or (45, 85, 150)
        self.text_color    = text_color
        self.font          = font_manager.get(font_size, bold=True)
        self.border_radius = border_radius
        self.icon          = icon

        self.hovered  = False
        self.pressed  = False
        self._anim    = 0.0    # 0..1 hover animation

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mx, my)
        target = 1.0 if self.hovered else 0.0
        self._anim += (target - self._anim) * min(dt * 10, 1.0)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

    def draw(self, surface):
        t = self._anim
        # Màu nền thay đổi khi hover
        r = int(self.base_color[0] + (60*t))
        g = int(self.base_color[1] + (40*t))
        b = int(self.base_color[2] + (30*t))
        clr = (min(r,255), min(g,255), min(b,255))

        # Scale nhẹ khi hover
        scale  = 1.0 + 0.02 * t
        w      = int(self.rect.width  * scale)
        h      = int(self.rect.height * scale)
        x      = self.rect.centerx - w // 2
        y      = self.rect.centery - h // 2
        drawn  = pygame.Rect(x, y, w, h)

        # Bóng
        shadow = pygame.Rect(drawn.x+3, drawn.y+4, drawn.width, drawn.height)
        pygame.draw.rect(surface, (10,10,20), shadow, border_radius=self.border_radius)

        # Thân nút
        pygame.draw.rect(surface, clr, drawn, border_radius=self.border_radius)

        # Viền sáng trên
        highlight_surf = pygame.Surface((drawn.width, 4), pygame.SRCALPHA)
        highlight_surf.fill((255,255,255,40))
        surface.blit(highlight_surf, (drawn.x, drawn.y+self.border_radius//2))

        # Viền
        border_c = (min(clr[0]+50,255), min(clr[1]+50,255), min(clr[2]+50,255))
        pygame.draw.rect(surface, border_c, drawn, 2,
                         border_radius=self.border_radius)

        # Text
        txt = self.font.render(self.text, True, self.text_color)
        surface.blit(txt, txt.get_rect(center=drawn.center))


# ════════════════════════════════════════════════════════════════
#  PARTICLE NỀN MENU (TINH TÚ BAY)
# ════════════════════════════════════════════════════════════════

class MenuStar:
    def __init__(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.r = random.uniform(1, 3)
        self.speed = random.uniform(5, 20)
        self.alpha = random.randint(80, 200)
        self.w, self.h = w, h

    def update(self, dt):
        self.y += self.speed * dt
        if self.y > self.h:
            self.y = 0
            self.x = random.uniform(0, self.w)

    def draw(self, surface):
        s = pygame.Surface((int(self.r*2)+2, int(self.r*2)+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (200, 220, 255, self.alpha),
                           (int(self.r)+1, int(self.r)+1), int(self.r))
        surface.blit(s, (int(self.x)-int(self.r), int(self.y)-int(self.r)))


# ════════════════════════════════════════════════════════════════
#  MENU CHÍNH
# ════════════════════════════════════════════════════════════════

class MenuScreen:
    def __init__(self, screen):
        self.screen = screen
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT

        self.font_title = font_manager.get(52, bold=True)
        self.font_sub   = font_manager.get(20)
        self.font_sm    = font_manager.get(14)

        bw, bh = 260, 55
        cx = W // 2
        self.btn_play     = Button((cx-bw//2, 300, bw, bh), ">>  Bắt Đầu Chơi",
                                    (40, 120, 60), font_size=20)
        self.btn_highscore= Button((cx-bw//2, 370, bw, bh), "*  Bảng Điểm Cao",
                                    (100, 90, 20), font_size=20)
        self.btn_editor   = Button((cx-bw//2, 440, bw, bh), "[]  Map Editor",
                                    (60, 60, 130), font_size=20)
        self.btn_quit     = Button((cx-bw//2, 510, bw, bh), "X  Thoát",
                                    (110, 35, 35), font_size=20)
        self.buttons = [self.btn_play, self.btn_highscore,
                        self.btn_editor, self.btn_quit]

        # Stars
        self.stars = [MenuStar(W, H) for _ in range(120)]

        # Animation
        self._time = 0.0

    def update(self, dt):
        self._time += dt
        for s in self.stars:
            s.update(dt)
        for b in self.buttons:
            b.update(dt)

    def handle_event(self, event):
        if self.btn_play.is_clicked(event):      return 'level_select'
        if self.btn_highscore.is_clicked(event): return 'highscore'
        if self.btn_editor.is_clicked(event):    return 'editor'
        if self.btn_quit.is_clicked(event):      return 'quit'
        return None

    def draw(self):
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        # Gradient nền
        for y in range(H):
            ratio = y / H
            r = int(10 + 20*ratio)
            g = int(15 + 30*ratio)
            b = int(30 + 50*ratio)
            pygame.draw.line(self.screen, (r,g,b), (0,y), (W,y))

        # Stars
        for s in self.stars:
            s.draw(self.screen)

        # Tiêu đề
        t = self._time
        glow = abs(math.sin(t * 1.5))

        # Shadow tiêu đề
        shadow = self.font_title.render("PathFinder TD", True, (20, 40, 80))
        self.screen.blit(shadow, shadow.get_rect(center=(W//2+3, 183)))

        # Title chính với gradient effect
        clr = (int(120+80*glow), int(180+60*glow), 255)
        title = self.font_title.render("PathFinder TD", True, clr)
        self.screen.blit(title, title.get_rect(center=(W//2, 180)))

        # Subtitle
        sub = self.font_sub.render("BFS Tower Defense - IT003 UIT", True,
                                    (140, 170, 220))
        self.screen.blit(sub, sub.get_rect(center=(W//2, 235)))

        # Đường phân cách
        pygame.draw.line(self.screen, (60, 100, 160),
                         (W//2-150, 265), (W//2+150, 265), 2)

        # Buttons
        for b in self.buttons:
            b.draw(self.screen)

        # Footer
        foot = self.font_sm.render("Nguyễn Minh Khang – MSSV: 25520793", True,
                                    (80, 100, 130))
        self.screen.blit(foot, foot.get_rect(
            center=(W//2, H-25)))


# ════════════════════════════════════════════════════════════════
#  MÀN CHỌN LEVEL
# ════════════════════════════════════════════════════════════════

class LevelSelectScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_lg = font_manager.get(34, bold=True)
        self.font_md = font_manager.get(17, bold=True)
        self.font_sm = font_manager.get(14)

        self.btn_back = Button((30, 30, 130, 45), "<- Quay lại",
                                (50, 50, 100), font_size=15)

        self._build_level_cards()

    def _build_level_cards(self):
        from level import get_all_levels
        from save_manager import get_best_score, is_level_unlocked
        self.levels = get_all_levels()
        self.cards   = []
        W = WINDOW_WIDTH

        for i, lv in enumerate(self.levels):
            cw, ch = 340, 200
            cx = W//2 - cw//2 + (i-1)*380
            cy = WINDOW_HEIGHT//2 - ch//2
            unlocked = is_level_unlocked(lv['id'])
            best     = get_best_score(lv['id'])
            self.cards.append({
                'level':    lv,
                'rect':     pygame.Rect(cx, cy, cw, ch),
                'unlocked': unlocked,
                'best':     best,
                'hovered':  False,
            })

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        for card in self.cards:
            card['hovered'] = card['rect'].collidepoint(mx, my)
        self.btn_back.update(dt)

    def handle_event(self, event):
        if self.btn_back.is_clicked(event):
            return ('back', None)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for card in self.cards:
                if card['unlocked'] and card['rect'].collidepoint(event.pos):
                    return ('play', card['level']['id'])
        return None

    def draw(self):
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        # Nền
        for y in range(H):
            ratio = y / H
            r = int(8 + 15*ratio)
            g = int(12 + 20*ratio)
            b = int(25 + 40*ratio)
            pygame.draw.line(self.screen, (r,g,b), (0,y), (W,y))

        # Tiêu đề
        title = self.font_lg.render("Chọn Màn Chơi", True, (180, 210, 255))
        self.screen.blit(title, title.get_rect(center=(W//2, 80)))

        # Cards
        for card in self.cards:
            self._draw_card(card)

        self.btn_back.draw(self.screen)

    def _draw_card(self, card):
        lv   = card['level']
        rect = card['rect']
        hovs = card['hovered'] and card['unlocked']

        # Bóng
        shadow = pygame.Rect(rect.x+4, rect.y+5, rect.width, rect.height)
        pygame.draw.rect(self.screen, (5,5,15), shadow, border_radius=16)

        # Nền card
        if card['unlocked']:
            base_c = (25, 35, 60) if not hovs else (35, 50, 90)
        else:
            base_c = (20, 20, 30)
        pygame.draw.rect(self.screen, base_c, rect, border_radius=16)

        # Viền màu chủ đề
        border_c = lv['diff_color'] if card['unlocked'] else C_DARK_GRAY
        pygame.draw.rect(self.screen, border_c, rect, 2, border_radius=16)

        if not card['unlocked']:
            # Màn bị khóa
            lock = self.font_lg.render("[LOCKED]", True, C_DARK_GRAY)
            self.screen.blit(lock, lock.get_rect(center=(rect.centerx, rect.centery-15)))
            lbl = self.font_sm.render("Hoan thanh man truoc de mo", True, C_GRAY)
            self.screen.blit(lbl, lbl.get_rect(center=(rect.centerx, rect.bottom-25)))
            return

        x, y = rect.x + 15, rect.y + 15

        # Số màn
        num = self.font_lg.render(f"Màn {lv['id']}", True, (200, 220, 255))
        self.screen.blit(num, (x, y))

        # Tên màn
        name = self.font_md.render(lv['name'], True, lv['diff_color'])
        self.screen.blit(name, (x, y + 40))

        # Độ khó
        diff = self.font_sm.render(f"Độ khó: {lv['difficulty']}", True, lv['diff_color'])
        self.screen.blit(diff, (x, y + 68))

        # Mô tả
        for i, line in enumerate(lv['desc'].split('\n')):
            d = self.font_sm.render(line, True, C_GRAY)
            self.screen.blit(d, (x, y + 95 + i*20))

        # Điểm cao nhất
        if card['best'] > 0:
            best = self.font_sm.render(f"Điểm cao: {card['best']:,}", True, C_GOLD)
            self.screen.blit(best, (x, rect.bottom - 30))


# ════════════════════════════════════════════════════════════════
#  HUD (THANH THÔNG TIN TRONG GAME)
# ════════════════════════════════════════════════════════════════

class HUD:
    def __init__(self, screen):
        self.screen  = screen
        self.font_lg = font_manager.get(20, bold=True)
        self.font_md = font_manager.get(15, bold=True)
        self.font_sm = font_manager.get(13)

    def draw(self, hp, max_hp, gold, score, wave_text, wave_idx,
             break_timer=0.0, speed=1):
        W = WINDOW_WIDTH

        # Nền HUD
        pygame.draw.rect(self.screen, C_HUD_BG,
                         pygame.Rect(0, 0, W, HUD_HEIGHT))
        pygame.draw.line(self.screen, C_PANEL_BORDER,
                         (0, HUD_HEIGHT-1), (W, HUD_HEIGHT-1), 2)

        # ── HP ──
        hp_ratio = hp / max(max_hp, 1)
        hp_color = (C_HP_FULL if hp_ratio > 0.6 else
                    C_HP_MED  if hp_ratio > 0.3 else C_HP_LOW)

        # Icon tim
        self._draw_heart(self.screen, 28, HUD_HEIGHT//2 - 2)
        # Text
        hp_txt = self.font_lg.render(f"{hp} / {max_hp}", True, hp_color)
        self.screen.blit(hp_txt, (50, HUD_HEIGHT//2 - hp_txt.get_height()//2))

        # Bar HP
        bar_x, bar_y = 160, HUD_HEIGHT//2 - 6
        bar_w, bar_h = 120, 12
        pygame.draw.rect(self.screen, (40,40,50),
                         pygame.Rect(bar_x, bar_y, bar_w, bar_h),
                         border_radius=3)
        fill = int(bar_w * hp_ratio)
        if fill > 0:
            pygame.draw.rect(self.screen, hp_color,
                             pygame.Rect(bar_x, bar_y, fill, bar_h),
                             border_radius=3)

        # ── VÀNG ──
        gold_txt = self.font_lg.render(f"Gold: {gold}", True, C_GOLD)
        self.screen.blit(gold_txt,
                         (310, HUD_HEIGHT//2 - gold_txt.get_height()//2))

        # ── ĐIỂM ──
        score_txt = self.font_md.render(f"Điểm: {score:,}", True, (200, 220, 255))
        self.screen.blit(score_txt,
                         (W//2 - 60, HUD_HEIGHT//2 - score_txt.get_height()//2))

        # ── WAVE ──
        if break_timer > 1.0:
            wave_str = f"Wave {wave_idx+1} trong: {break_timer:.1f}s"
            wc = C_GOLD
        else:
            wave_str = wave_text
            wc = (200, 220, 255)
        wave_txt = self.font_md.render(wave_str, True, wc)
        self.screen.blit(wave_txt,
                         (W - 300, HUD_HEIGHT//2 - wave_txt.get_height()//2))

        # Tốc độ
        sp_txt = self.font_sm.render(f"x{speed}", True, C_GRAY)
        self.screen.blit(sp_txt, (W - 50, HUD_HEIGHT//2 - sp_txt.get_height()//2))

    def _draw_heart(self, surface, cx, cy):
        """Vẽ trái tim đơn giản."""
        # Dùng polygon hình tim
        pts = []
        for i in range(30):
            t = math.radians(i * 12)
            x = 16 * math.sin(t)**3
            y = -(13*math.cos(t) - 5*math.cos(2*t)
                   - 2*math.cos(3*t) - math.cos(4*t))
            pts.append((cx + x*1.1, cy + y*1.1))
        pygame.draw.polygon(surface, (220, 50, 80), pts)
        pygame.draw.polygon(surface, (255, 120, 140), pts, 1)


# ════════════════════════════════════════════════════════════════
#  PANEL BÊN PHẢI (CHỌN THÁP)
# ════════════════════════════════════════════════════════════════

class TowerPanel:
    """
    Panel 320px bên phải màn hình.
    Hiển thị 3 loại tháp để người dùng chọn mua.
    Khi click tháp → người dùng click lên lưới để xây.
    """

    def __init__(self, screen):
        self.screen        = screen
        self.selected_type = None    # Loại tháp đang được chọn
        self.selected_tower= None    # Tháp đang được click trên lưới

        self.font_lg = font_manager.get(17, bold=True)
        self.font_md = font_manager.get(14, bold=True)
        self.font_sm = font_manager.get(12)

        # Vị trí các card tháp
        self._card_rects = {}
        self._build_cards()

        self.btn_sell = Button(
            (PANEL_X + 20, WINDOW_HEIGHT - 70, PANEL_WIDTH-40, 45),
            "$  Bán Tháp",
            (120, 60, 20), font_size=15
        )

        self.btn_cancel = Button(
            (PANEL_X + 20, WINDOW_HEIGHT - 75, PANEL_WIDTH-40, 45),
            "X  Hủy",
            (80, 25, 25), font_size=15
        )

        self._time = 0.0
        self.wave_btn = Button(
            (PANEL_X + 20, HUD_HEIGHT + 10, PANEL_WIDTH-40, 40),
            ">> Gọi Wave",
            (30, 80, 140), font_size=15
        )

    def _build_cards(self):
        x = PANEL_X + 10
        y = HUD_HEIGHT + 65
        w = PANEL_WIDTH - 20
        h = 120

        for i, ttype in enumerate(TOWER_TYPES):
            rect = pygame.Rect(x, y + i*(h+8), w, h)
            self._card_rects[ttype] = rect

    def update(self, dt, gold):
        self._time += dt
        self.btn_sell.update(dt)
        self.btn_cancel.update(dt)
        self.wave_btn.update(dt)
        self._gold = gold

    def handle_event(self, event, gold):
        """
        Xử lý click trong panel.

        Trả về:
            ('select', type)  – Chọn loại tháp
            ('cancel',)       – Hủy chọn
            ('sell',)         – Bán tháp đang chọn
            ('wave',)         – Bắt đầu wave sớm
            None
        """
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        # Nút wave
        if self.wave_btn.is_clicked(event):
            return ('wave',)

        # Cards tháp
        for ttype, rect in self._card_rects.items():
            if rect.collidepoint(event.pos):
                data = TOWER_DATA[ttype]
                if gold >= data['cost']:
                    if self.selected_type == ttype:
                        self.selected_type = None
                        return ('cancel',)
                    self.selected_type = ttype
                    self.selected_tower = None
                    return ('select', ttype)

        # Nút bán
        if self.selected_tower and self.btn_sell.is_clicked(event):
            return ('sell',)

        # Nút hủy
        if self.selected_type and self.btn_cancel.is_clicked(event):
            self.selected_type = None
            return ('cancel',)

        return None

    def draw(self, gold, wave_manager):
        # Nền panel
        panel = pygame.Rect(PANEL_X, HUD_HEIGHT, PANEL_WIDTH,
                            WINDOW_HEIGHT - HUD_HEIGHT)
        pygame.draw.rect(self.screen, C_PANEL_BG, panel)
        pygame.draw.line(self.screen, C_PANEL_BORDER,
                         (PANEL_X, HUD_HEIGHT), (PANEL_X, WINDOW_HEIGHT), 2)

        # Nút wave
        state = wave_manager.state if wave_manager else 'idle'
        if state == 'idle' and not (wave_manager and wave_manager.is_done):
            self.wave_btn.draw(self.screen)

        # Tiêu đề
        lbl = self.font_lg.render("=== THÁP ===", True, (180, 200, 240))
        self.screen.blit(lbl,
                         lbl.get_rect(center=(PANEL_X + PANEL_WIDTH//2,
                                              HUD_HEIGHT + 55)))

        # Cards
        for ttype in TOWER_TYPES:
            self._draw_tower_card(ttype, gold)

        # Info tháp đang chọn trên lưới
        if self.selected_tower:
            self._draw_tower_info(self.selected_tower)
            self.btn_sell.draw(self.screen)
        elif self.selected_type:
            self.btn_cancel.draw(self.screen)

    def _draw_tower_card(self, ttype, gold):
        rect  = self._card_rects[ttype]
        data  = TOWER_DATA[ttype]
        sel   = (self.selected_type == ttype)
        can   = (gold >= data['cost'])

        mx, my = pygame.mouse.get_pos()
        hov    = rect.collidepoint(mx, my)

        # Nền card
        if sel:
            bg = (40, 60, 100)
        elif hov and can:
            bg = (30, 45, 75)
        elif not can:
            bg = (20, 20, 28)
        else:
            bg = (22, 28, 45)
        pygame.draw.rect(self.screen, bg, rect, border_radius=10)

        # Viền
        border = data['color'] if (sel or (hov and can)) else (40,50,70)
        pygame.draw.rect(self.screen, border, rect, 2, border_radius=10)

        # Preview tháp
        draw_tower_preview(self.screen, ttype,
                           rect.x + 38, rect.centery)

        # Tên
        txt = self.font_md.render(data['name'], True,
                                   data['color'] if can else C_DARK_GRAY)
        self.screen.blit(txt, (rect.x + 72, rect.y + 10))

        # Stats
        stats = [
            (f"DMG: {data['damage']}",   (220, 100, 100)),
            (f"Tầm: {data['range']}",    (100, 180, 220)),
            (f"Tốc: {data['fire_rate']}/s", (180, 220, 100)),
        ]
        for i, (s, c) in enumerate(stats):
            surf = self.font_sm.render(s, True, c if can else C_DARK_GRAY)
            self.screen.blit(surf, (rect.x + 72, rect.y + 35 + i*22))

        # Giá
        cost_c = C_GOLD if can else C_RED
        cost   = self.font_md.render(f"{data['cost']}g", True, cost_c)
        self.screen.blit(cost, (rect.right - cost.get_width() - 10,
                                 rect.bottom - cost.get_height() - 8))

        # Tag "Không đủ tiền"
        if not can:
            no = self.font_sm.render("Không đủ vàng", True, C_RED)
            self.screen.blit(no, (rect.x + 72, rect.bottom - 22))

    def _draw_tower_info(self, tower):
        """Hiển thị thông tin tháp đang được chọn."""
        y = WINDOW_HEIGHT - 220
        x = PANEL_X + 12

        pygame.draw.rect(self.screen, (20, 28, 48),
                         pygame.Rect(PANEL_X+8, y-5, PANEL_WIDTH-16, 150),
                         border_radius=8)
        pygame.draw.rect(self.screen, tower.color,
                         pygame.Rect(PANEL_X+8, y-5, PANEL_WIDTH-16, 150),
                         1, border_radius=8)

        lbl = self.font_md.render("Tháp đã chọn:", True, C_GRAY)
        self.screen.blit(lbl, (x, y))

        name = self.font_lg.render(tower.name, True, tower.color)
        self.screen.blit(name, (x, y+22))

        info = tower.get_info()
        rows = [
            (f"Hạ: {info['kills']} quái", (200, 255, 200)),
            (f"Tổng sát thương: {tower.total_damage}", (255, 200, 100)),
            (f"Tầm bắn: {info['range']} ô", (100, 180, 255)),
            (f"Bán được: {info['sell']}g", C_GOLD),
        ]
        for i, (s, c) in enumerate(rows):
            surf = self.font_sm.render(s, True, c)
            self.screen.blit(surf, (x, y + 50 + i*22))


# ════════════════════════════════════════════════════════════════
#  PAUSE OVERLAY
# ════════════════════════════════════════════════════════════════

class PauseOverlay:
    def __init__(self, screen):
        self.screen   = screen
        self.font_lg  = font_manager.get(44, bold=True)
        self.font_sm  = font_manager.get(17)
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT

        self.btn_resume = Button((W//2-130, H//2+20,  260, 55),
                                  ">> Tiếp Tục", (40,120,60), font_size=20)
        self.btn_menu   = Button((W//2-130, H//2+90,  260, 55),
                                  "<< Menu Chính", (60,60,130), font_size=20)
        self.buttons = [self.btn_resume, self.btn_menu]

    def update(self, dt):
        for b in self.buttons:
            b.update(dt)

    def handle_event(self, event):
        if self.btn_resume.is_clicked(event): return 'resume'
        if self.btn_menu.is_clicked(event):   return 'menu'
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            return 'resume'
        return None

    def draw(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        txt = self.font_lg.render("TẠM DỪNG", True, (200, 220, 255))
        self.screen.blit(txt, txt.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2-60)))
        hint = self.font_sm.render("Nhấn  P  để tiếp tục", True, C_GRAY)
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2-10)))

        for b in self.buttons:
            b.draw(self.screen)


# ════════════════════════════════════════════════════════════════
#  GAME OVER
# ════════════════════════════════════════════════════════════════

class GameOverScreen:
    def __init__(self, screen):
        self.screen  = screen
        self.font_lg = font_manager.get(52, bold=True)
        self.font_md = font_manager.get(20)
        self.font_sm = font_manager.get(15)
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT

        self.btn_retry = Button((W//2-130, H//2+60, 260, 55),
                                 "<< Chơi Lại", (40,90,40), font_size=20)
        self.btn_menu  = Button((W//2-130, H//2+130, 260, 55),
                                 "<< Menu Chính", (60,60,130), font_size=20)
        self.buttons   = [self.btn_retry, self.btn_menu]
        self._time     = 0.0
        self.score_data = None

    def set_data(self, score, wave, kills):
        self.score_data = {'score': score, 'wave': wave, 'kills': kills}

    def update(self, dt):
        self._time += dt
        for b in self.buttons:
            b.update(dt)

    def handle_event(self, event):
        if self.btn_retry.is_clicked(event): return 'retry'
        if self.btn_menu.is_clicked(event):  return 'menu'
        return None

    def draw(self):
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Pulsing red title
        glow = abs(math.sin(self._time * 2))
        clr  = (int(200+55*glow), int(40*glow), int(40*glow))
        txt  = self.font_lg.render("THẤT BẠI", True, clr)
        self.screen.blit(txt, txt.get_rect(center=(W//2, H//2 - 120)))

        sub = self.font_md.render("Căn cứ của bạn đã bị chiếm!", True,
                                   (200, 120, 120))
        self.screen.blit(sub, sub.get_rect(center=(W//2, H//2 - 60)))

        if self.score_data:
            d = self.score_data
            lines = [
                f"Điểm: {d['score']:,}",
                f"Đến wave: {d['wave']}",
                f"Quái đã hạ: {d['kills']}",
            ]
            for i, line in enumerate(lines):
                s = self.font_sm.render(line, True, C_GRAY)
                self.screen.blit(s, s.get_rect(center=(W//2, H//2-10+i*28)))

        for b in self.buttons:
            b.draw(self.screen)


# ════════════════════════════════════════════════════════════════
#  VICTORY SCREEN
# ════════════════════════════════════════════════════════════════

class VictoryScreen:
    def __init__(self, screen):
        self.screen  = screen
        self.font_lg = font_manager.get(52, bold=True)
        self.font_md = font_manager.get(20)
        self.font_sm = font_manager.get(15)
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT

        self.btn_next  = Button((W//2-130, H//2+70, 260, 55),
                                 ">> Màn Tiếp Theo", (40,100,40), font_size=20)
        self.btn_menu  = Button((W//2-130, H//2+140, 260, 55),
                                 "<< Menu Chính", (60,60,130), font_size=20)
        self.buttons   = [self.btn_next, self.btn_menu]
        self._time     = 0.0
        self.score_data= None
        self.rank      = None
        self.has_next  = True
        # Fireworks particles
        self._particles = []
        self._fw_timer  = 0.0

    def set_data(self, score, wave, kills, rank, has_next=True):
        self.score_data = {'score': score, 'wave': wave, 'kills': kills}
        self.rank  = rank
        self.has_next = has_next
        if not has_next:
            self.btn_next.text = "Chơi Lại"

    def _spawn_firework(self):
        import random
        cx = random.randint(100, WINDOW_WIDTH-100)
        cy = random.randint(80, 350)
        clr = random.choice([(255,200,50),(100,200,255),(255,100,200),
                               (100,255,150),(255,150,50)])
        for _ in range(20):
            import math as m
            angle = m.radians(random.uniform(0,360))
            speed = random.uniform(80,200)
            vx = speed * m.cos(angle)
            vy = speed * m.sin(angle)
            from particle import Particle
            self._particles.append(
                Particle(cx,cy,vx,vy,clr,random.uniform(0.6,1.4),
                          random.randint(3,7), gravity=80))

    def update(self, dt):
        self._time     += dt
        self._fw_timer -= dt
        if self._fw_timer <= 0:
            self._spawn_firework()
            self._fw_timer = 0.4
        for p in self._particles:
            p.update(dt)
        self._particles = [p for p in self._particles if not p.dead]
        for b in self.buttons:
            b.update(dt)

    def handle_event(self, event):
        if self.btn_next.is_clicked(event):
            return 'next' if self.has_next else 'retry'
        if self.btn_menu.is_clicked(event): return 'menu'
        return None

    def draw(self):
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 195))
        self.screen.blit(overlay, (0, 0))

        # Bắn pháo hoa
        for p in self._particles:
            p.draw(self.screen)

        # Title nhấp nháy vàng
        glow = abs(math.sin(self._time * 2))
        clr  = (int(200+55*glow), int(180+60*glow), int(40*glow))
        txt  = self.font_lg.render("CHIẾN THẮNG!", True, clr)
        self.screen.blit(txt, txt.get_rect(center=(W//2, H//2 - 130)))

        sub = self.font_md.render("Căn cứ được bảo vệ thành công!", True,
                                   (180, 255, 180))
        self.screen.blit(sub, sub.get_rect(center=(W//2, H//2 - 70)))

        if self.score_data:
            d = self.score_data
            lines = [
                f"Điểm: {d['score']:,}",
                f"Quái đã hạ: {d['kills']}",
            ]
            if self.rank and self.rank <= 3:
                lines.append(f"🏆 Top {self.rank} bảng điểm!")
            for i, line in enumerate(lines):
                c = C_GOLD if 'Top' in line else C_GRAY
                s = self.font_sm.render(line, True, c)
                self.screen.blit(s, s.get_rect(center=(W//2, H//2-5+i*28)))

        for b in self.buttons:
            b.draw(self.screen)


# ════════════════════════════════════════════════════════════════
#  BẢNG ĐIỂM CAO
# ════════════════════════════════════════════════════════════════

class HighscoreScreen:
    def __init__(self, screen):
        self.screen   = screen
        self.font_lg  = pygame.font.SysFont('Arial', 34, bold=True)
        self.font_md  = pygame.font.SysFont('Arial', 18, bold=True)
        self.font_sm  = pygame.font.SysFont('Arial', 15)
        self.selected_level = 1

        W = WINDOW_WIDTH
        self.btn_back = Button((30, 30, 120, 45), "← Quay lại",
                                (50,50,100), font_size=16)
        self.tab_btns = [
            Button((W//2 - 200 + i*140, 100, 120, 40), f"Màn {i+1}",
                    (40,50,90), font_size=14)
            for i in range(3)
        ]

    def update(self, dt):
        self.btn_back.update(dt)
        for b in self.tab_btns:
            b.update(dt)

    def handle_event(self, event):
        if self.btn_back.is_clicked(event): return 'back'
        for i, b in enumerate(self.tab_btns):
            if b.is_clicked(event):
                self.selected_level = i + 1
        return None

    def draw(self):
        from save_manager import get_highscores
        W, H = WINDOW_WIDTH, WINDOW_HEIGHT
        for y in range(H):
            ratio = y/H
            pygame.draw.line(self.screen, (int(8+15*ratio),int(12+20*ratio),int(25+40*ratio)),(0,y),(W,y))

        title = self.font_lg.render("Bảng Điểm Cao", True, C_GOLD)
        self.screen.blit(title, title.get_rect(center=(W//2, 55)))

        # Tabs
        for i, b in enumerate(self.tab_btns):
            if self.selected_level == i+1:
                b.base_color = (80, 110, 180)
            else:
                b.base_color = (40, 50, 90)
            b.draw(self.screen)

        # Bảng điểm
        scores = get_highscores(self.selected_level)
        y_start = 170

        headers = ["#", "Điểm", "Wave", "Kết quả", "Ngày"]
        cols    = [80, 200, 350, 480, 620]
        for i, h in enumerate(headers):
            s = self.font_md.render(h, True, C_GOLD)
            self.screen.blit(s, (cols[i], y_start))

        pygame.draw.line(self.screen, C_DARK_GRAY,
                         (60, y_start+28), (W-60, y_start+28), 1)

        if not scores:
            no = self.font_md.render("Chưa có dữ liệu", True, C_GRAY)
            self.screen.blit(no, no.get_rect(center=(W//2, y_start+80)))
        else:
            for i, entry in enumerate(scores):
                y = y_start + 40 + i*38
                rank_c = [C_GOLD, (200,200,200), (180,120,60)] if i < 3 else [C_GRAY]
                rc = rank_c[min(i, len(rank_c)-1)]

                vals = [
                    f"#{i+1}",
                    f"{entry['score']:,}",
                    f"{entry['wave']}",
                    "✓ Thắng" if entry.get('victory') else "✗ Thua",
                    entry.get('date',''),
                ]
                for j, v in enumerate(vals):
                    vc = C_GREEN if '✓' in v else (C_RED if '✗' in v else rc if j==0 else C_WHITE)
                    s = self.font_sm.render(v, True, vc)
                    self.screen.blit(s, (cols[j], y))

        self.btn_back.draw(self.screen)
