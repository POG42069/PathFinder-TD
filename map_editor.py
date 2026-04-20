"""
map_editor.py - Trình chỉnh sửa bản đồ tùy chỉnh
Môn: IT003 - Cấu trúc dữ liệu và Giải thuật - UIT

Người dùng có thể:
  - Vẽ/xóa vật cản trên lưới
  - Đặt điểm spawn và base
  - Lưu bản đồ ra file JSON
  - Tải bản đồ từ file JSON
  - Kiểm tra đường BFS còn hợp lệ không
"""

import pygame
import json
import os
import font_manager
from settings import *
from bfs import bfs, has_path
from grid import Grid


class MapEditor:
    """
    Trình chỉnh sửa bản đồ trong game.

    Chế độ vẽ (draw_mode):
        'obstacle'  – Click để thêm/xóa vật cản cố định
        'spawn'     – Click để đặt điểm xuất hiện quái
        'base'      – Click để đặt căn cứ

    Phím tắt:
        1 – Chế độ vật cản
        2 – Chế độ spawn
        3 – Chế độ base
        S – Lưu bản đồ
        L – Tải bản đồ
        C – Xóa toàn bộ
        V – Kiểm tra BFS
        ESC – Thoát editor
    """

    def __init__(self, screen):
        self.screen    = screen
        self.draw_mode = 'obstacle'
        self.is_drawing = False

        self.obstacles = set()
        self.spawn_pos = (5, 0)
        self.base_pos  = (5, 14)

        self.bfs_path  = []
        self._recalc_bfs()

        self.font_sm = font_manager.get(13)
        self.font_md = font_manager.get(14, bold=True)
        self.font_lg = font_manager.get(20, bold=True)

        self.message      = ""
        self.message_timer = 0.0
        self.message_color = C_WHITE

        self._history: list[set] = []

        self.current_file = ""

        self._map_files = self._scan_maps()

        os.makedirs(MAPS_DIR, exist_ok=True)


    def _recalc_bfs(self):
        """Tính lại đường BFS với cấu hình hiện tại."""
        grid_data = self._build_grid_data()
        self.bfs_path = bfs(grid_data, self.spawn_pos, self.base_pos,
                            GRID_ROWS, GRID_COLS)

    def _build_grid_data(self):
        """Tạo ma trận 2D từ trạng thái editor."""
        g = [[CELL_EMPTY]*GRID_COLS for _ in range(GRID_ROWS)]
        sr, sc = self.spawn_pos
        br, bc = self.base_pos
        g[sr][sc] = CELL_SPAWN
        g[br][bc] = CELL_BASE
        for (r, c) in self.obstacles:
            if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                g[r][c] = CELL_OBSTACLE
        return g


    def handle_event(self, event):
        """
        Xử lý sự kiện người dùng.

        Trả về:
            str hoặc None:
                'quit'   – Thoát editor
                'menu'   – Về menu
                None     – Tiếp tục
        """
        if event.type == pygame.KEYDOWN:
            return self._handle_key(event.key)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.is_drawing = True
                self._save_history()
                self._handle_click(*event.pos)
            elif event.button == 3:
                pos = self._pixel_to_cell(*event.pos)
                if pos:
                    self.obstacles.discard(pos)
                    self._recalc_bfs()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_drawing = False

        elif event.type == pygame.MOUSEMOTION:
            if self.is_drawing and self.draw_mode == 'obstacle':
                self._handle_click(*event.pos)

        return None

    def _handle_key(self, key):
        if key == pygame.K_ESCAPE:
            return 'menu'
        elif key == pygame.K_1:
            self.draw_mode = 'obstacle'
            self._show_msg("Chế độ: Vật cản", C_GRAY)
        elif key == pygame.K_2:
            self.draw_mode = 'spawn'
            self._show_msg("Chế độ: Điểm Spawn", C_SPAWN_CLR)
        elif key == pygame.K_3:
            self.draw_mode = 'base'
            self._show_msg("Chế độ: Căn Cứ", C_BASE_CLR)
        elif key == pygame.K_s:
            self._save_map()
        elif key == pygame.K_l:
            self._load_map()
        elif key == pygame.K_c:
            self._clear_all()
        elif key == pygame.K_v:
            self._verify_path()
        elif key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self._undo()
        return None

    def _handle_click(self, mx, my):
        """Xử lý click/kéo trên lưới."""
        cell = self._pixel_to_cell(mx, my)
        if not cell:
            return
        r, c = cell

        if self.draw_mode == 'obstacle':
            if cell == self.spawn_pos or cell == self.base_pos:
                return
            if cell in self.obstacles:
                self.obstacles.discard(cell)
            else:
                self.obstacles.add(cell)
                if not has_path(self._build_grid_data(),
                                self.spawn_pos, self.base_pos,
                                GRID_ROWS, GRID_COLS):
                    self.obstacles.discard(cell)
                    self._show_msg("Vật cản chặn hết đường đi!", C_RED)
                    return
            self._recalc_bfs()

        elif self.draw_mode == 'spawn':
            if cell == self.base_pos or cell in self.obstacles:
                return
            self.spawn_pos = cell
            self._recalc_bfs()
            self._show_msg(f"Spawn: {cell}", C_SPAWN_CLR)

        elif self.draw_mode == 'base':
            if cell == self.spawn_pos or cell in self.obstacles:
                return
            self.base_pos = cell
            self._recalc_bfs()
            self._show_msg(f"Base: {cell}", C_BASE_CLR)


    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt

    def draw(self):
        """Vẽ toàn bộ màn hình editor."""
        self.screen.fill(C_BG)

        self._draw_grid()

        self._draw_panel()

        if self.message and self.message_timer > 0:
            alpha = min(int(255 * self.message_timer / 2.0), 255)
            surf  = self.font_md.render(self.message, True, self.message_color)
            surf.set_alpha(alpha)
            self.screen.blit(surf,
                             (GRID_WIDTH//2 - surf.get_width()//2,
                              GRID_OFFSET_Y + 10))

    def _draw_grid(self):
        """Vẽ lưới với các ô đã chỉnh sửa."""
        path_set = set(self.bfs_path)

        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                x = GRID_OFFSET_X + c * CELL_SIZE
                y = GRID_OFFSET_Y + r * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pos  = (r, c)

                if pos == self.spawn_pos:
                    color = (160, 30, 30)
                elif pos == self.base_pos:
                    color = (30, 80, 180)
                elif pos in self.obstacles:
                    color = C_OBSTACLE
                elif pos in path_set:
                    idx   = self.bfs_path.index(pos)
                    ratio = idx / max(len(self.bfs_path)-1, 1)
                    color = (int(200+55*ratio), int(155-50*ratio), 50)
                elif (r + c) % 2 == 0:
                    color = C_GRASS
                else:
                    color = C_GRASS_ALT

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, C_GRID_LINE, rect, 1)

                if pos == self.spawn_pos:
                    lbl = self.font_sm.render("S", True, C_WHITE)
                    self.screen.blit(lbl, lbl.get_rect(center=rect.center))
                elif pos == self.base_pos:
                    lbl = self.font_sm.render("B", True, C_WHITE)
                    self.screen.blit(lbl, lbl.get_rect(center=rect.center))

        mx, my = pygame.mouse.get_pos()
        cell   = self._pixel_to_cell(mx, my)
        if cell:
            hx = GRID_OFFSET_X + cell[1]*CELL_SIZE
            hy = GRID_OFFSET_Y + cell[0]*CELL_SIZE
            hover = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            hover.fill((255, 255, 255, 50))
            self.screen.blit(hover, (hx, hy))

    def _draw_panel(self):
        """Vẽ panel thông tin bên phải."""
        panel = pygame.Rect(PANEL_X, 0, PANEL_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, C_PANEL_BG, panel)
        pygame.draw.line(self.screen, C_PANEL_BORDER,
                         (PANEL_X, 0), (PANEL_X, WINDOW_HEIGHT), 2)

        x = PANEL_X + 10
        y = 80

        def txt(s, clr=C_WHITE, font=None):
            nonlocal y
            f = font or self.font_sm
            surf = f.render(s, True, clr)
            self.screen.blit(surf, (x, y))
            y += surf.get_height() + 4

        txt("MAP EDITOR", C_GOLD, self.font_lg)
        y += 10

        mode_colors = {'obstacle': C_GRAY, 'spawn': C_SPAWN_CLR, 'base': C_BASE_CLR}
        mode_names  = {'obstacle': 'Vật cản [1]', 'spawn': 'Spawn [2]', 'base': 'Base [3]'}
        txt("Chế độ:", C_WHITE, self.font_md)
        txt(f"  {mode_names[self.draw_mode]}",
            mode_colors[self.draw_mode], self.font_md)
        y += 10

        txt("─" * 26, C_DARK_GRAY)
        txt("Phím tắt:", C_WHITE, self.font_md)
        cmds = [
            ("1", "Vẽ vật cản"),
            ("2", "Đặt Spawn"),
            ("3", "Đặt Base"),
            ("S", "Lưu bản đồ"),
            ("L", "Tải bản đồ"),
            ("C", "Xóa tất cả"),
            ("V", "Kiểm tra BFS"),
            ("Ctrl+Z", "Hoàn tác"),
            ("ESC", "Thoát editor"),
        ]
        for key_, desc in cmds:
            k_surf = self.font_sm.render(f"[{key_}]", True, C_GOLD)
            d_surf = self.font_sm.render(desc, True, C_GRAY)
            self.screen.blit(k_surf, (x, y))
            self.screen.blit(d_surf, (x + k_surf.get_width() + 6, y))
            y += 20

        y += 10
        txt("─" * 26, C_DARK_GRAY)
        txt("Thông tin:", C_WHITE, self.font_md)
        txt(f"  Spawn: {self.spawn_pos}", C_SPAWN_CLR)
        txt(f"  Base : {self.base_pos}", C_BASE_CLR)
        txt(f"  Vật cản: {len(self.obstacles)}", C_GRAY)

        if self.bfs_path:
            txt(f"  BFS path: {len(self.bfs_path)} bước", C_GREEN)
        else:
            txt("  BFS: KHÔNG CÓ ĐƯỜNG!", C_RED, self.font_md)

        if self.current_file:
            y += 10
            txt(f"  File: {os.path.basename(self.current_file)}", C_GRAY)


    def _save_map(self, filename=None):
        """Lưu bản đồ ra file JSON."""
        if filename is None:
            import datetime
            ts  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(MAPS_DIR, f"map_{ts}.json")

        data = {
            "spawn":     list(self.spawn_pos),
            "base":      list(self.base_pos),
            "obstacles": [list(p) for p in self.obstacles],
        }
        try:
            os.makedirs(MAPS_DIR, exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            self.current_file = filename
            self._show_msg(f"Đã lưu: {os.path.basename(filename)}", C_GREEN)
        except IOError as e:
            self._show_msg(f"Lỗi lưu: {e}", C_RED)

    def _load_map(self, filename=None):
        """Tải bản đồ từ file JSON."""
        if filename is None:
            files = self._scan_maps()
            if not files:
                self._show_msg("Không có file bản đồ!", C_RED)
                return
            filename = files[-1]

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.spawn_pos = tuple(data["spawn"])
            self.base_pos  = tuple(data["base"])
            self.obstacles = {tuple(p) for p in data["obstacles"]}
            self.current_file = filename
            self._recalc_bfs()
            self._show_msg(f"Đã tải: {os.path.basename(filename)}", C_GREEN)
        except (IOError, KeyError, json.JSONDecodeError) as e:
            self._show_msg(f"Lỗi tải: {e}", C_RED)

    def _scan_maps(self):
        """Quét danh sách file map trong thư mục."""
        os.makedirs(MAPS_DIR, exist_ok=True)
        files = [os.path.join(MAPS_DIR, f)
                 for f in os.listdir(MAPS_DIR)
                 if f.endswith('.json')]
        return sorted(files)

    def get_level_data(self):
        """Xuất dữ liệu bản đồ để dùng trong game."""
        return {
            'spawn':     self.spawn_pos,
            'base':      self.base_pos,
            'obstacles': list(self.obstacles),
        }


    def _pixel_to_cell(self, mx, my):
        """Chuyển pixel sang ô lưới."""
        if mx >= PANEL_X or my < GRID_OFFSET_Y:
            return None
        c = (mx - GRID_OFFSET_X) // CELL_SIZE
        r = (my - GRID_OFFSET_Y) // CELL_SIZE
        if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
            return (r, c)
        return None

    def _verify_path(self):
        if self.bfs_path:
            self._show_msg(f"BFS hợp lệ: {len(self.bfs_path)} bước", C_GREEN)
        else:
            self._show_msg("Không tìm thấy đường đi!", C_RED)

    def _clear_all(self):
        self._save_history()
        self.obstacles.clear()
        self._recalc_bfs()
        self._show_msg("Đã xóa tất cả vật cản", C_GRAY)

    def _save_history(self):
        self._history.append(frozenset(self.obstacles))
        if len(self._history) > 20:
            self._history.pop(0)

    def _undo(self):
        if self._history:
            self.obstacles = set(self._history.pop())
            self._recalc_bfs()
            self._show_msg("Hoàn tác", C_GRAY)

    def _show_msg(self, msg, color=C_WHITE, duration=2.0):
        self.message       = msg
        self.message_color = color
        self.message_timer = duration
