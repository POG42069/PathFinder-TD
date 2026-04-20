"""
main.py - Entry point cho PathFinder TD
=========================================
Môn   : IT003 - Cấu trúc dữ liệu và Giải thuật
Trường: Đại học Công nghệ Thông tin (UIT)
Tác giả: Nguyễn Minh Khang – MSSV: 25520793

Mô tả:
    Game Tower Defense 2D sử dụng thuật toán BFS (Breadth-First Search)
    được tự implement để pathFinding quái vật trên lưới 2D.
    Mỗi khi người chơi xây tháp, BFS tự động tính lại đường đi ngắn nhất.

Chạy: python main.py
Yêu cầu: Python 3.8+, pygame >= 2.0
"""

import sys
import pygame
import font_manager
from settings import *



class App:
    """
    Lớp App điều phối toàn bộ game:
        – Khởi tạo pygame
        – Quản lý chuyển đổi giữa các màn hình (state machine)
        – Vòng lặp chính (main loop)

    State machine:
        menu → level_select → playing
                                 ↓
                           game_over / victory → menu / retry / next
        menu → editor
        menu → highscore
    """

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        font_manager.init()

        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        self.clock      = pygame.time.Clock()
        self.state      = STATE_MENU
        self.running    = True

        self.current_level_id = 1
        self._level_data      = None

        self._menu           = None
        self._level_select   = None
        self._game_session   = None
        self._map_editor     = None
        self._highscore      = None

        self._init_menu()


    def _init_menu(self):
        from ui import MenuScreen
        self._menu = MenuScreen(self.screen)
        self.state = STATE_MENU

    def _init_level_select(self):
        from ui import LevelSelectScreen
        self._level_select = LevelSelectScreen(self.screen)
        self.state = STATE_LEVEL_SELECT

    def _init_game(self, level_id):
        from level import get_level
        from game import GameSession
        self.current_level_id = level_id
        self._level_data      = get_level(level_id)
        if not self._level_data:
            print(f"[ERROR] Không tìm thấy level {level_id}")
            self._init_menu()
            return
        self._game_session = GameSession(self.screen, self._level_data)
        self.state = STATE_PLAYING

    def _init_editor(self):
        from map_editor import MapEditor
        self._map_editor = MapEditor(self.screen)
        self.state = STATE_EDITOR

    def _init_highscore(self):
        from ui import HighscoreScreen
        self._highscore = HighscoreScreen(self.screen)
        self.state = STATE_HIGHSCORE


    def run(self):
        """Vòng lặp game chính."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                self._dispatch_event(event)

            self._dispatch_update(dt)

            self._dispatch_draw()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


    def _dispatch_event(self, event):
        """Chuyển event đến màn hình đang hoạt động."""
        s = self.state

        if s == STATE_MENU:
            result = self._menu.handle_event(event)
            if result == 'level_select': self._init_game(1)
            elif result == 'highscore':  self._init_highscore()
            elif result == 'editor':     self._init_editor()
            elif result == 'quit':       self.running = False

        elif s == STATE_LEVEL_SELECT:
            result = self._level_select.handle_event(event)
            if result is None:
                return
            cmd, arg = result
            if cmd == 'back': self._init_menu()
            elif cmd == 'play': self._init_game(arg)

        elif s == STATE_PLAYING:
            gs = self._game_session
            if gs.result in ('game_over', 'victory'):
                nav = gs.handle_end_event(event)
                if nav == 'retry':
                    self._init_game(self.current_level_id)
                elif nav == 'menu':
                    self._init_menu()
                elif nav == 'next':
                    self._init_menu()
            else:
                gs.handle_event(event)
                if gs.result == 'menu':
                    self._init_menu()

        elif s == STATE_EDITOR:
            result = self._map_editor.handle_event(event)
            if result == 'menu':
                self._init_menu()

        elif s == STATE_HIGHSCORE:
            result = self._highscore.handle_event(event)
            if result == 'back':
                self._init_menu()

    def _dispatch_update(self, dt):
        """Cập nhật màn hình đang hoạt động."""
        s = self.state

        if s == STATE_MENU:
            self._menu.update(dt)

        elif s == STATE_LEVEL_SELECT:
            self._level_select.update(dt)

        elif s == STATE_PLAYING:
            gs = self._game_session
            if gs.result in ('game_over', 'victory'):
                gs.update_end_screen(dt)
            else:
                gs.update(dt)
                if gs.result == 'menu':
                    self._init_menu()

        elif s == STATE_EDITOR:
            self._map_editor.update(dt)

        elif s == STATE_HIGHSCORE:
            self._highscore.update(dt)

    def _dispatch_draw(self):
        """Vẽ màn hình đang hoạt động."""
        s = self.state

        if s == STATE_MENU:
            self._menu.draw()

        elif s == STATE_LEVEL_SELECT:
            self._level_select.draw()

        elif s == STATE_PLAYING:
            self._game_session.draw()

        elif s == STATE_EDITOR:
            self._map_editor.draw()

        elif s == STATE_HIGHSCORE:
            self._highscore.draw()



if __name__ == '__main__':
    app = App()
    app.run()
