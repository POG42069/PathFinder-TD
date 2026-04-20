"""
grid.py - Lớp quản lý bản đồ lưới 2D
Môn: IT003 - Cấu trúc dữ liệu và Giải thuật - UIT
"""

import pygame
import font_manager
from settings import *
from bfs import bfs, has_path


class Grid:
    """
    Lớp quản lý bản đồ lưới 2D cho game Tower Defense.

    Mỗi ô (cell) trong lưới có một trạng thái:
        CELL_EMPTY    = 0  – Trống, có thể xây tháp hoặc quái đi qua
        CELL_BLOCKED  = 1  – Có tháp, BFS không đi qua
        CELL_SPAWN    = 2  – Điểm xuất hiện quái
        CELL_BASE     = 3  – Căn cứ (đích đến)
        CELL_OBSTACLE = 4  – Địa hình cố định

    Thuật toán BFS được gọi lại mỗi khi lưới thay đổi
    (xây/phá tháp) để tính toán lại đường đi cho quái.
    """

    def __init__(self, rows, cols, spawn_pos, base_pos, obstacles=None):
        """
        Khởi tạo lưới.

        Tham số:
            rows (int)      : Số hàng.
            cols (int)      : Số cột.
            spawn_pos (tuple): Tọa độ (row, col) điểm spawn.
            base_pos  (tuple): Tọa độ (row, col) căn cứ.
            obstacles (list) : Danh sách tọa độ vật cản cố định.
        """
        self.rows  = rows
        self.cols  = cols
        self.spawn = spawn_pos
        self.base  = base_pos

        # ── Ma trận trạng thái ──────────────────────────────────
        # Khởi tạo toàn bộ là EMPTY
        self.cells = [[CELL_EMPTY] * cols for _ in range(rows)]

        # Đặt điểm spawn và base
        r, c = spawn_pos
        self.cells[r][c] = CELL_SPAWN
        r, c = base_pos
        self.cells[r][c] = CELL_BASE

        # Đặt các vật cản cố định
        if obstacles:
            for (or_, oc) in obstacles:
                self.cells[or_][oc] = CELL_OBSTACLE

        # ── Đường đi hiện tại (do BFS tính) ────────────────────
        self.path = []
        self._recalculate_path()

        # ── Tháp đã xây ─────────────────────────────────────────
        # Dict: (row, col) → tower object
        self.towers = {}

        # ── Sprite / Surface vẽ ─────────────────────────────────
        self._tile_surf = None          # cache surface bản đồ tĩnh

        # Hiệu ứng highlight
        self.hover_cell  = None         # Ô đang hover
        self.selected_type = None       # Loại tháp đang chọn để xây

    # ════════════════════════════════════════════════════════════
    #  PATHFINDING (BFS)
    # ════════════════════════════════════════════════════════════

    def _recalculate_path(self):
        """
        Gọi BFS để tính lại đường ngắn nhất từ spawn → base.
        Cập nhật self.path. Được gọi sau mỗi thay đổi lưới.
        """
        self.path = bfs(self.cells, self.spawn, self.base,
                        self.rows, self.cols)

    def get_path(self):
        """Trả về đường đi hiện tại (list of (row, col))."""
        return self.path

    def get_random_path(self, start=None):
        """Gọi lại BFS để sinh ra một đường đi ngẫu nhiên từ vị trí xuất phát cho trước (hoặc spawn mặc định)."""
        if start is None:
            start = self.spawn
        from bfs import bfs
        return bfs(self.cells, start, self.base, self.rows, self.cols)

    def has_valid_path(self):
        """Kiểm tra có đường đi hợp lệ không."""
        return len(self.path) > 1

    # ════════════════════════════════════════════════════════════
    #  QUẢN LÝ THÁP
    # ════════════════════════════════════════════════════════════

    def can_build(self, row, col):
        """
        Kiểm tra có thể xây tháp tại (row, col) không.

        Điều kiện:
          1. Trong giới hạn lưới.
          2. Ô đang EMPTY (không phải spawn, base, obstacle, tháp sẵn).
          3. Sau khi đặt tháp tạm, BFS vẫn tìm được đường.

        Trả về:
            bool: True nếu hợp lệ.
        """
        # Kiểm tra giới hạn
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False
        # Kiểm tra ô trống
        if self.cells[row][col] != CELL_EMPTY:
            return False

        # Thử đặt tháp tạm → chạy BFS xem đường đi còn không
        self.cells[row][col] = CELL_BLOCKED
        path_exists = has_path(self.cells, self.spawn, self.base,
                               self.rows, self.cols)
        # Hoàn tác tạm
        self.cells[row][col] = CELL_EMPTY

        return path_exists

    def place_tower(self, row, col, tower_obj):
        """
        Đặt tháp vào ô (row, col) và tính lại đường đi.

        Trả về:
            bool: True nếu thành công.
        """
        if not self.can_build(row, col):
            return False
        self.cells[row][col] = CELL_BLOCKED
        self.towers[(row, col)] = tower_obj
        self._recalculate_path()
        return True

    def remove_tower(self, row, col):
        """
        Phá tháp tại (row, col) và tính lại đường đi.

        Trả về:
            tower_obj hoặc None nếu không có tháp.
        """
        if (row, col) not in self.towers:
            return None
        tower = self.towers.pop((row, col))
        self.cells[row][col] = CELL_EMPTY
        self._recalculate_path()
        return tower

    def get_tower_at(self, row, col):
        """Lấy tháp tại ô (row, col), hoặc None."""
        return self.towers.get((row, col))

    def all_towers(self):
        """Trả về danh sách tất cả tower objects."""
        return list(self.towers.values())

    # ════════════════════════════════════════════════════════════
    #  CHUYỂN ĐỔI TỌA ĐỘ
    # ════════════════════════════════════════════════════════════

    def cell_to_pixel(self, row, col):
        """
        Chuyển tọa độ ô lưới sang pixel (góc trên-trái của ô).

        Trả về:
            tuple(int, int): (x, y) pixel.
        """
        x = GRID_OFFSET_X + col * CELL_SIZE
        y = GRID_OFFSET_Y + row * CELL_SIZE
        return x, y

    def cell_center_pixel(self, row, col):
        """Trả về tọa độ pixel tâm của ô."""
        x, y = self.cell_to_pixel(row, col)
        return x + CELL_SIZE // 2, y + CELL_SIZE // 2

    def pixel_to_cell(self, px, py):
        """
        Chuyển tọa độ pixel sang ô lưới.

        Trả về:
            tuple(int, int) hoặc None nếu ngoài lưới.
        """
        col = (px - GRID_OFFSET_X) // CELL_SIZE
        row = (py - GRID_OFFSET_Y) // CELL_SIZE
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return row, col
        return None

    # ════════════════════════════════════════════════════════════
    #  VẼ
    # ════════════════════════════════════════════════════════════

    def draw(self, surface, show_path=True):
        """
        Vẽ toàn bộ lưới lên surface.

        Tham số:
            surface   : pygame.Surface đích.
            show_path : Có hiển thị đường đi BFS không.
        """
        path_set = set(self.path) if show_path else set()

        for row in range(self.rows):
            for col in range(self.cols):
                x, y = self.cell_to_pixel(row, col)
                rect  = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                state = self.cells[row][col]
                pos   = (row, col)

                # ── Màu nền ô ──
                if state == CELL_OBSTACLE:
                    color = C_OBSTACLE
                elif state == CELL_SPAWN:
                    color = (180, 30, 30)
                elif state == CELL_BASE:
                    color = (30, 80, 180)
                elif state == CELL_BLOCKED:
                    # Ô có tháp – vẽ nền tối (tháp tự vẽ ở trên)
                    color = (25, 30, 45)

                elif (row + col) % 2 == 0:
                    color = C_GRASS
                else:
                    color = C_GRASS_ALT

                pygame.draw.rect(surface, color, rect)

                # ── Kẻ lưới ──
                pygame.draw.rect(surface, C_GRID_LINE, rect, 1)

                # ── Nhãn spawn / base ──
                if state == CELL_SPAWN:
                    self._draw_spawn(surface, rect)
                elif state == CELL_BASE:
                    self._draw_base(surface, rect)
                elif state == CELL_OBSTACLE:
                    self._draw_obstacle(surface, rect)

        # ── Hover highlight khi người dùng đang chọn xây ──
        if self.hover_cell and self.selected_type:
            hr, hc = self.hover_cell
            hx, hy = self.cell_to_pixel(hr, hc)
            hrect  = pygame.Rect(hx, hy, CELL_SIZE, CELL_SIZE)
            valid  = self.can_build(hr, hc)

            overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            if valid:
                overlay.fill((100, 255, 100, 90))
            else:
                overlay.fill((255, 60, 60, 90))
            surface.blit(overlay, (hx, hy))
            clr = C_GREEN if valid else C_RED
            pygame.draw.rect(surface, clr, hrect, 2)

    # ── Vẽ điểm spawn ────────────────────────────────────────────

    def _draw_spawn(self, surface, rect):
        cx, cy = rect.centerx, rect.centery
        r = CELL_SIZE // 2 - 6

        # Vòng tròn đỏ phát sáng
        for i in range(4, 0, -1):
            alpha_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surf, (255, 80, 80, 40 * i),
                               (CELL_SIZE//2, CELL_SIZE//2), r + i*4)
            surface.blit(alpha_surf, rect.topleft)

        pygame.draw.circle(surface, (255, 100, 100), (cx, cy), r)
        pygame.draw.circle(surface, (255, 200, 200), (cx, cy), r, 2)

        # Dấu "S"
        font = font_manager.get(18, bold=True)
        txt  = font.render("S", True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=(cx, cy)))

    # ── Vẽ căn cứ ────────────────────────────────────────────────

    def _draw_base(self, surface, rect):
        cx, cy = rect.centerx, rect.centery

        # Vòng sáng xanh
        for i in range(4, 0, -1):
            alpha_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surf, (60, 130, 255, 35 * i),
                               (CELL_SIZE//2, CELL_SIZE//2), 24 + i*3)
            surface.blit(alpha_surf, rect.topleft)

        # Ngôi sao / biểu tượng căn cứ
        self._draw_star(surface, cx, cy, 20, 10, 5,
                        (80, 160, 255), (180, 210, 255))
        font = pygame.font.SysFont('Arial', 11, bold=True)
        txt  = font.render("BASE", True, (200, 230, 255))
        surface.blit(txt, txt.get_rect(center=(cx, cy + 18)))

    def _draw_star(self, surface, cx, cy, r_outer, r_inner, n_points,
                   color_fill, color_border):
        """Vẽ ngôi sao n cánh."""
        import math
        pts = []
        for i in range(n_points * 2):
            angle = math.pi / n_points * i - math.pi / 2
            r     = r_outer if i % 2 == 0 else r_inner
            pts.append((cx + r * math.cos(angle),
                         cy + r * math.sin(angle)))
        pygame.draw.polygon(surface, color_fill, pts)
        pygame.draw.polygon(surface, color_border, pts, 2)

    # ── Vẽ vật cản ───────────────────────────────────────────────

    def _draw_obstacle(self, surface, rect):
        """Vẽ khối đá/vật cản với hiệu ứng 3D đơn giản."""
        x, y = rect.x + 4, rect.y + 4
        w, h = CELL_SIZE - 8, CELL_SIZE - 8

        # Bóng
        pygame.draw.rect(surface, (30, 30, 38),
                         pygame.Rect(x+3, y+3, w, h), border_radius=6)
        # Khối đá
        pygame.draw.rect(surface, (75, 78, 90),
                         pygame.Rect(x, y, w, h), border_radius=6)
        # Viền sáng
        pygame.draw.rect(surface, (110, 115, 130),
                         pygame.Rect(x, y, w, h), 2, border_radius=6)
        # Điểm highlight góc
        pygame.draw.rect(surface, (130, 135, 150),
                         pygame.Rect(x+4, y+4, w//3, 4), border_radius=2)
