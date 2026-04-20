"""
game.py - Logic game chính và quản lý trạng thái
Môn: IT003 - Cấu trúc dữ liệu và Giải thuật - UIT
"""

import pygame
import math
import font_manager
from settings import *
from grid import Grid
from tower import create_tower
from wave import WaveManager
from particle import (update_particles, draw_particles,
                      spawn_base_hit_particles, spawn_gold_text)
from ui import HUD, TowerPanel, PauseOverlay
import save_manager


class GameSession:
    """
    Quản lý một phiên chơi game đầy đủ.

    Mỗi màn chơi (level) tạo một GameSession mới.
    Session bao gồm: lưới, tháp, quái, wave, HUD, panel.

    Vòng lặp chính:
        handle_event → update → draw

    Trả về kết quả qua self.result:
        None       – Đang chơi
        'menu'     – Về menu
        'retry'    – Chơi lại
        'next'     – Màn tiếp theo
        'game_over'
        'victory'
    """

    def __init__(self, screen, level_data):
        """
        Tham số:
            screen     (pygame.Surface): Màn hình chính.
            level_data (dict)          : Dữ liệu màn (từ level.py).
        """
        self.screen  = screen
        self.level   = level_data
        self.result  = None

        self.grid = Grid(
            rows      = GRID_ROWS,
            cols      = GRID_COLS,
            spawn_pos = level_data['spawn'],
            base_pos  = level_data['base'],
            obstacles  = level_data.get('obstacles', []),
        )

        self.hp       = level_data.get('starting_hp',   STARTING_HP)
        self.max_hp   = self.hp
        self.gold     = level_data.get('starting_gold', STARTING_GOLD)
        self.score    = 0
        self.kills    = 0
        self.paused   = False
        self.speed    = 1

        self.wave_mgr = WaveManager()

        self.projectiles = []
        self.particles   = []

        self.hud         = HUD(screen)
        self.tower_panel = TowerPanel(screen)
        self.pause_overlay = PauseOverlay(screen)

        self.selected_tower_obj = None
        self.hover_cell         = None

        self.font_notify = font_manager.get(18, bold=True)

        self._notify      = ""
        self._notify_timer = 0.0
        self._notify_color = C_WHITE

        self.wave_mgr.break_timer = 2.0
        self.wave_mgr.state       = 'break'


    def handle_event(self, event):
        if self.paused:
            result = self.pause_overlay.handle_event(event)
            if result == 'resume':
                self.paused = False
            elif result == 'menu':
                self.result = 'menu'
            return

        if event.type == pygame.KEYDOWN:
            self._handle_key(event.key)
            return

        panel_result = self.tower_panel.handle_event(event, self.gold)
        if panel_result:
            self._handle_panel_action(panel_result)
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_grid_click(event)

    def _handle_key(self, key):
        if key == pygame.K_p:
            self.paused = not self.paused
        elif key == pygame.K_ESCAPE:
            if self.tower_panel.selected_type or self.selected_tower_obj:
                self.tower_panel.selected_type  = None
                self.tower_panel.selected_tower = None
                self.selected_tower_obj          = None
                self.grid.selected_type          = None
            else:
                self.result = 'menu'
        elif key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            self.speed = 2
            self._notify_msg("Tốc độ x2", C_GOLD)
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.speed = 1
            self._notify_msg("Tốc độ x1", C_WHITE)
        elif key == pygame.K_SPACE:
            if self.wave_mgr.state == 'idle':
                self._start_wave()

    def _handle_panel_action(self, action):
        cmd = action[0]
        if cmd == 'select':
            self.tower_panel.selected_type   = action[1]
            self.tower_panel.selected_tower  = None
            self.selected_tower_obj          = None
            self.grid.selected_type          = action[1]
        elif cmd == 'cancel':
            self.tower_panel.selected_type   = None
            self.grid.selected_type          = None
        elif cmd == 'sell':
            self._sell_tower()
        elif cmd == 'wave':
            self._start_wave()

    def _handle_grid_click(self, event):
        if event.button != 1:
            return
        mx, my = event.pos
        cell = self.grid.pixel_to_cell(mx, my)
        if not cell:
            return
        row, col = cell

        if self.tower_panel.selected_type:
            self._try_place_tower(row, col)
        else:
            tower = self.grid.get_tower_at(row, col)
            if tower:
                self.selected_tower_obj          = tower
                self.tower_panel.selected_tower  = tower
                self.tower_panel.selected_type   = None
            else:
                self.selected_tower_obj          = None
                self.tower_panel.selected_tower  = None

    def _try_place_tower(self, row, col):
        """Thử xây tháp tại (row, col)."""
        ttype = self.tower_panel.selected_type
        data  = TOWER_DATA[ttype]
        cost  = data['cost']

        if self.gold < cost:
            self._notify_msg("Không đủ vàng!", C_RED)
            return

        tower = create_tower(ttype, row, col)
        success = self.grid.place_tower(row, col, tower)

        if success:
            self.gold -= cost
            for enemy in self.wave_mgr.enemies:
                enemy.update_path_from_current(self.grid)
            self._notify_msg(f"Đã xây {data['name']}", data['color'])
        else:
            self._notify_msg("Không thể xây ở đây!", C_RED)

    def _sell_tower(self):
        """Bán tháp đang chọn."""
        t = self.selected_tower_obj
        if not t:
            return
        removed = self.grid.remove_tower(t.row, t.col)
        if removed:
            self.gold += removed.sell_value
            for enemy in self.wave_mgr.enemies:
                enemy.update_path_from_current(self.grid)
            self._notify_msg(f"Bán được {removed.sell_value}g", C_GOLD)
        self.selected_tower_obj         = None
        self.tower_panel.selected_tower = None

    def _start_wave(self):
        if self.wave_mgr.can_start_wave():
            self.wave_mgr.start_next_wave(self.grid)


    def update(self, dt):
        if self.paused or self.result:
            if self.paused:
                self.pause_overlay.update(dt)
            return

        dt_fast = dt * self.speed

        self.wave_mgr.update(dt_fast, self.grid,
                              on_wave_complete=self._on_wave_complete)

        for tower in self.grid.all_towers():
            tower.update(dt_fast, self.wave_mgr.enemies, self.projectiles)

        for proj in self.projectiles:
            proj.update(dt_fast, self.wave_mgr.enemies,
                        self.particles,
                        self._on_gold_earned,
                        self._on_kill)
        self.projectiles = [p for p in self.projectiles if not p.dead]

        reached = []
        for enemy in self.wave_mgr.enemies:
            if enemy.reached_base:
                reached.append(enemy)

        for enemy in reached:
            self.hp -= enemy.base_damage
            bx, by = self.grid.cell_center_pixel(*self.grid.base)
            spawn_base_hit_particles(self.particles, bx, by)
            self._notify_msg(f"-{enemy.base_damage} HP!", C_RED, 0.8)
            if self.hp <= 0:
                self.hp = 0
                self._end_game(victory=False)
                return

        update_particles(self.particles, dt_fast)

        if self._notify_timer > 0:
            self._notify_timer -= dt

        mx, my = pygame.mouse.get_pos()
        cell = self.grid.pixel_to_cell(mx, my)
        self.grid.hover_cell = cell

        self.tower_panel.update(dt, self.gold)
        self.tower_panel.selected_type
        self.grid.selected_type = self.tower_panel.selected_type

        if (self.wave_mgr.state == 'done' and
                self.wave_mgr.all_enemies_dead and
                self.result is None):
            self._end_game(victory=True)

    def _on_gold_earned(self, amount):
        self.gold += amount
        spawn_gold_text(self.particles,
                        self.grid.cell_center_pixel(*self.grid.base)[0],
                        self.grid.cell_center_pixel(*self.grid.base)[1] - 30,
                        amount)

    def _on_kill(self):
        self.score += KILL_SCORE
        self.kills  += 1

    def _on_wave_complete(self, completed_wave_idx):
        self.score += WAVE_BONUS_SCORE
        if not self.wave_mgr.is_done:
            self._notify_msg(
                f"Wave {completed_wave_idx} hoàn thành! +{WAVE_BONUS_SCORE} điểm",
                C_GOLD, 2.5)

    def _end_game(self, victory):
        """Kết thúc game: lưu điểm, đặt result."""
        wave_reached = self.wave_mgr.wave_idx + (1 if victory else 0)
        rank = save_manager.submit_score(
            self.level['id'], self.score,
            wave_reached, victory)
        save_manager.update_kills(self.kills)

        if victory:
            from ui import VictoryScreen
            self._end_screen = VictoryScreen(self.screen)
            has_next = (self.level['id'] < 3)
            self._end_screen.set_data(self.score,
                                       wave_reached,
                                       self.kills, rank, has_next)
            self.result = 'victory'
        else:
            from ui import GameOverScreen
            self._end_screen = GameOverScreen(self.screen)
            self._end_screen.set_data(self.score, wave_reached, self.kills)
            self.result = 'game_over'

    def _notify_msg(self, msg, color=C_WHITE, duration=1.5):
        self._notify       = msg
        self._notify_color = color
        self._notify_timer = duration


    def draw(self):
        self.screen.fill(C_BG)

        show_path = True
        self.grid.draw(self.screen, show_path=show_path)

        for tower in self.grid.all_towers():
            tower.draw(self.screen)

        if self.selected_tower_obj and not self.selected_tower_obj.dead if hasattr(self.selected_tower_obj, 'dead') else False:
            pass
        if self.selected_tower_obj:
            self.selected_tower_obj.draw_range(self.screen)

        for enemy in self.wave_mgr.enemies:
            enemy.draw(self.screen)

        for proj in self.projectiles:
            proj.draw(self.screen)

        draw_particles(self.particles, self.screen)

        wt   = self.wave_mgr.get_progress_text()
        brkT = self.wave_mgr.get_break_timer()
        self.hud.draw(self.hp, self.max_hp, self.gold, self.score,
                       wt, self.wave_mgr.wave_idx, brkT, self.speed)

        self.tower_panel.draw(self.gold, self.wave_mgr)

        if self._notify and self._notify_timer > 0:
            alpha = int(255 * min(self._notify_timer, 0.5) / 0.5)
            surf  = self.font_notify.render(self._notify, True,
                                             self._notify_color)
            surf.set_alpha(alpha)
            self.screen.blit(surf,
                             surf.get_rect(center=(GRID_WIDTH//2,
                                                    HUD_HEIGHT + 30)))

        if self.paused:
            self.pause_overlay.draw()
        elif self.result in ('game_over', 'victory'):
            self._end_screen.draw()


    def handle_end_event(self, event):
        """Xử lý event trên màn kết thúc."""
        if not hasattr(self, '_end_screen'):
            return None
        res = self._end_screen.handle_event(event)
        if res == 'retry':  return 'retry'
        if res == 'menu':   return 'menu'
        if res == 'next':   return 'next'
        return None

    def update_end_screen(self, dt):
        if hasattr(self, '_end_screen'):
            self._end_screen.update(dt)
