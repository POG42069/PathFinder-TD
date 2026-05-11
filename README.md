<h1 align="center">🏰 PathFinder TD – BFS Tower Defense</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Pygame-2.0%2B-green?logo=pygame" alt="Pygame">
  <img src="https://img.shields.io/badge/NumPy-1.24%2B-orange?logo=numpy" alt="NumPy">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
  <img src="https://img.shields.io/badge/M%C3%B4n-IT003%20CTDL%26GT-purple" alt="IT003">
</p>

<p align="center">
  <b>Game Tower Defense 2D</b> sử dụng thuật toán <b>BFS (Breadth-First Search)</b> tự implement<br>
  để tìm đường đi ngắn nhất cho quái vật trên bản đồ lưới 2D.
</p>

---

## 📋 Thông tin đồ án

| Thông tin | Chi tiết |
|-----------|----------|
| **Môn học** | IT003 – Cấu trúc dữ liệu và Giải thuật |
| **Trường** | Đại học Công nghệ Thông tin – ĐHQG TP.HCM (UIT) |
| **Tác giả** | Nguyễn Minh Khang |
| **MSSV** | 25520793 |
| **Ngôn ngữ** | Python 3.8+ |
| **Framework** | Pygame 2.0+ |
| **Năm** | 2026 |

---

## 🎮 Mô tả game

**PathFinder TD** là game Tower Defense (Phòng thủ tháp) 2D, nơi người chơi xây dựng các tháp phòng thủ trên bản đồ lưới để ngăn chặn quái vật tiến về căn cứ.

### Điểm nổi bật – Thuật toán BFS tự implement

Điểm cốt lõi của game là **thuật toán BFS (Breadth-First Search)** được **tự implement hoàn toàn** (không sử dụng thư viện bên ngoài):

- **Cấu trúc dữ liệu Queue** – Tự viết bằng Python list, hỗ trợ các thao tác `enqueue`, `dequeue`, `peek`, `is_empty`
- **Thuật toán BFS** – Tìm đường đi ngắn nhất trên lưới 2D
- Mỗi khi người chơi **xây hoặc phá tháp**, BFS tự động **tính lại đường đi ngắn nhất**
- Người chơi có thể tạo **mê cung** bằng cách đặt tháp chiến lược, ép quái đi đường vòng

```
   BFS hoạt động:

   Spawn ──→ Duyệt 4 hướng (trên, dưới, trái, phải)
              │
              ├── Ô hợp lệ? → Thêm vào Queue
              │
              └── Ô đích (Base)? → Truy vết → Trả về path
```

---

## ✨ Tính năng chính

| # | Tính năng | Mô tả |
|---|-----------|-------|
| 1 | 🔍 **BFS Pathfinding** | Thuật toán BFS tự implement với Queue tự viết |
| 2 | 🏗️ **3 loại tháp** | Xạ Thủ (bắn nhanh), Đại Bác (AOE), Pháp Sư (tầm xa) |
| 3 | 👾 **3 loại quái** | Quỷ Lùn (nhanh), Orc (bền), Quái Khổng Lồ (siêu bền) |
| 4 | 🌊 **10 wave** | Độ khó tăng dần, hệ số nhân HP theo wave |
| 5 | 🗺️ **Ma trận mở** | Bản đồ lưới 15×10, tự do xây tháp tạo mê cung |
| 6 | 🎨 **Map Editor** | Trình chỉnh sửa bản đồ, vẽ vật cản, lưu/tải JSON |
| 7 | 🏆 **Bảng điểm cao** | Lưu top 5 điểm, thống kê kills, games |
| 8 | 💾 **Lưu game** | Auto-save điểm số và tiến trình |
| 9 | 🔊 **Âm thanh** | Sound effects tổng hợp (synthesized) cho mọi sự kiện |
| 10 | 💥 **Hiệu ứng hạt** | Particle system cho nổ, tia lửa, text damage |
| 11 | 🎯 **Hệ thống đạn** | Đạn bay theo mục tiêu với trail effect |
| 12 | 🇻🇳 **Hỗ trợ tiếng Việt** | Font manager tự động tìm font Unicode |

---

## 📁 Cấu trúc dự án

```
PathFinder TD/
├── main.py              # Entry point – Vòng lặp chính, state machine
├── game.py              # Logic game chính, quản lý phiên chơi
├── bfs.py               # ★ Thuật toán BFS & cấu trúc Queue (tự implement)
├── grid.py              # Quản lý bản đồ lưới 2D
├── tower.py             # Các lớp tháp phòng thủ (Archer, Cannon, Mage)
├── enemy.py             # Các lớp quái vật (Goblin, Orc, Troll)
├── wave.py              # Quản lý hệ thống wave (đợt quái)
├── projectile.py        # Hệ thống đạn bắn
├── particle.py          # Hiệu ứng hạt (particles)
├── ui.py                # Giao diện: Menu, HUD, Panel, GameOver, Victory
├── settings.py          # Cấu hình và hằng số toàn cục
├── level.py             # Định nghĩa các màn chơi
├── save_manager.py      # Quản lý lưu điểm cao và dữ liệu
├── font_manager.py      # Quản lý font hỗ trợ tiếng Việt
├── map_editor.py        # Trình chỉnh sửa bản đồ tùy chỉnh
├── sound_manager.py     # Hệ thống âm thanh (synthesized SFX)
├── generate_docs.py     # Script tạo tài liệu tự động
├── requirements.txt     # Danh sách thư viện cần cài
├── maps/                # Thư mục lưu bản đồ tùy chỉnh (JSON)
├── saves/               # Thư mục lưu điểm cao (JSON)
└── docs/                # Tài liệu API tự động (pydoc HTML)
```

---

## 🧠 Chi tiết thuật toán BFS

### Cấu trúc dữ liệu Queue (Hàng đợi)

Queue được tự implement trong file `bfs.py`, hoạt động theo nguyên tắc **FIFO (First In – First Out)**:

```python
class Queue:
    """Queue tự implement bằng Python list."""

    def enqueue(self, item):   # Thêm vào cuối – O(1)
    def dequeue(self):         # Lấy ra từ đầu – O(n)
    def peek(self):            # Xem đầu – O(1)
    def is_empty(self):        # Kiểm tra rỗng – O(1)
    def size(self):            # Số phần tử – O(1)
```

### Thuật toán BFS (Breadth-First Search)

```
Đầu vào: grid_data (ma trận 2D), start, end, rows, cols
Đầu ra:  Đường đi ngắn nhất [start, ..., end] hoặc []

1. Tạo Queue, enqueue(start)
2. Tạo visited = {start}, parent = {start: None}
3. WHILE Queue không rỗng:
   a. current = dequeue()
   b. NẾU current == end:
      → Truy vết parent ngược lại → Trả về path
   c. VỚI MỖI hướng (trên, dưới, trái, phải):
      - neighbor = current + direction
      - NẾU neighbor hợp lệ VÀ chưa thăm VÀ không bị chặn:
        → visited.add(neighbor)
        → parent[neighbor] = current
        → enqueue(neighbor)
4. Trả về [] (không có đường)
```

**Độ phức tạp:**
| | Thời gian | Không gian |
|---|-----------|------------|
| BFS | O(V + E) = O(rows × cols) | O(rows × cols) |
| Queue.enqueue | O(1) | – |
| Queue.dequeue | O(n) | – |

### Ứng dụng trong game

```
Spawn (S) ──BFS──→ Base (B)
    ↓
Người chơi xây tháp (T) → ô bị chặn
    ↓
BFS tính lại đường đi mới → quái đổi hướng
    ↓
Chiến thuật: Tạo mê cung dài → tháp bắn nhiều hơn!
```

---

## 🛡️ Hệ thống tháp

| Tháp | Tên | Sát thương | Tầm bắn | Tốc độ bắn | Giá | Đặc điểm |
|------|-----|-----------|---------|------------|-----|----------|
| 🟢 | Xạ Thủ (Archer) | 18 | 3.0 ô | 1.5/s | 50g | Bắn nhanh, ổn định |
| ⚫ | Đại Bác (Cannon) | 70 | 2.5 ô | 0.45/s | 100g | Sát thương cao, AOE |
| 🟣 | Pháp Sư (Mage) | 32 | 4.5 ô | 0.8/s | 125g | Tầm bắn xa nhất |

---

## 👾 Hệ thống quái

| Quái | Tên | HP | Tốc độ | Phần thưởng | Sát thương |
|------|-----|-----|--------|-------------|-----------|
| 🟢 | Quỷ Lùn (Goblin) | 90 | 2.8 | 10g | 1 |
| 🔴 | Orc Chiến Binh | 260 | 1.7 | 25g | 2 |
| 🔵 | Quái Khổng Lồ (Troll) | 700 | 1.0 | 60g | 5 |

> HP quái tăng 15% mỗi wave (hệ số: `1.0 + wave_idx × 0.15`)

---

## 🔊 Hệ thống âm thanh

Tất cả âm thanh được **tổng hợp bằng code** (synthesized) sử dụng numpy, không cần file audio bên ngoài:

| Sự kiện | Loại âm thanh |
|---------|---------------|
| Bắn cung (Archer) | Tiếng "twang" ngắn cao |
| Bắn pháo (Cannon) | Tiếng "boom" trầm |
| Phép thuật (Mage) | Tiếng "shimmer" ma thuật |
| Quái trúng đạn | Tiếng "thud" nhẹ |
| Quái chết | Tiếng nổ nhỏ |
| Quái chạm base | Cảnh báo nguy hiểm |
| Xây tháp | Tiếng "clink" xây dựng |
| Bán tháp | Tiếng coin drop |
| Bắt đầu wave | Tiếng kèn |
| Hoàn thành wave | Fanfare ngắn |
| Chiến thắng | Melody vui vẻ |
| Thua cuộc | Melody buồn |
| Click button | Tiếng "tick" nhẹ |

---

## ⚙️ Yêu cầu hệ thống & Thư viện

### Yêu cầu

- **Python**: 3.8 trở lên (khuyến nghị 3.12+)
- **Hệ điều hành**: Windows / macOS / Linux

### Thư viện cần cài đặt

| Thư viện | Phiên bản tối thiểu | Mục đích |
|----------|---------------------|----------|
| **pygame** | >= 2.0.0 | Engine game 2D: render đồ họa, xử lý sự kiện, phát âm thanh |
| **numpy** | >= 1.24.0 | Tổng hợp âm thanh (synthesize sine/square waves) |

> **Lưu ý**: Các module `json`, `os`, `math`, `random`, `sys`, `datetime`, `array` đều là **thư viện chuẩn Python** (standard library), không cần cài thêm.

### File `requirements.txt`

```
pygame>=2.0.0
numpy>=1.24.0
```

---

## 🚀 Cài đặt và chạy

### 1. Clone repository

```bash
git clone https://github.com/POG42069/PathFinder-TD.git
cd PathFinder-TD
```

### 2. Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 4. Chạy game

```bash
python main.py
```

---

## 🎮 Hướng dẫn chơi

### Luồng game

```
Menu Chính → Bắt Đầu Chơi → Gameplay → Chiến Thắng / Thua
    │                                        │
    ├── Bảng Điểm Cao                        ├── Chơi Lại
    └── Map Editor                           └── Menu Chính
```

### Cách chơi

1. **Chọn tháp** từ panel bên phải
2. **Click vào ô trống** trên lưới để xây tháp
3. **BFS tự động tính** đường đi mới cho quái
4. **Gọi wave** hoặc đợi tự động
5. **Bảo vệ căn cứ** khỏi quái vật!

### Phím tắt

| Phím | Chức năng |
|------|-----------|
| `P` | Tạm dừng / Tiếp tục |
| `ESC` | Thoát / Hủy chọn |
| `+` / `=` | Tăng tốc x2 |
| `-` | Tốc độ bình thường x1 |
| `SPACE` | Gọi wave sớm |

### Phím tắt Map Editor

| Phím | Chức năng |
|------|-----------|
| `1` | Chế độ vẽ vật cản |
| `2` | Đặt điểm Spawn |
| `3` | Đặt điểm Base |
| `S` | Lưu bản đồ |
| `L` | Tải bản đồ |
| `C` | Xóa tất cả |
| `V` | Kiểm tra BFS |
| `Ctrl+Z` | Hoàn tác |

---

## 📚 Tài liệu API (Documentation)

Tài liệu API chi tiết được tạo tự động từ docstring bằng **pydoc**, nằm trong thư mục `docs/`:

| File | Module | Mô tả |
|------|--------|-------|
| [`bfs.html`](docs/bfs.html) | `bfs` | Thuật toán BFS & Queue |
| [`grid.html`](docs/grid.html) | `grid` | Bản đồ lưới 2D |
| [`tower.html`](docs/tower.html) | `tower` | Các lớp tháp |
| [`enemy.html`](docs/enemy.html) | `enemy` | Các lớp quái vật |
| [`game.html`](docs/game.html) | `game` | Logic game chính |
| [`wave.html`](docs/wave.html) | `wave` | Hệ thống wave |
| [`projectile.html`](docs/projectile.html) | `projectile` | Hệ thống đạn |
| [`particle.html`](docs/particle.html) | `particle` | Hiệu ứng hạt |
| [`ui.html`](docs/ui.html) | `ui` | Giao diện người dùng |
| [`settings.html`](docs/settings.html) | `settings` | Cấu hình game |
| [`level.html`](docs/level.html) | `level` | Định nghĩa màn chơi |
| [`save_manager.html`](docs/save_manager.html) | `save_manager` | Lưu dữ liệu |
| [`font_manager.html`](docs/font_manager.html) | `font_manager` | Quản lý font |
| [`map_editor.html`](docs/map_editor.html) | `map_editor` | Trình chỉnh sửa bản đồ |
| [`sound_manager.html`](docs/sound_manager.html) | `sound_manager` | Hệ thống âm thanh |
| [`main.html`](docs/main.html) | `main` | Entry point |

### Tạo lại tài liệu

```bash
python generate_docs.py
```

---

## 🏗️ Kiến trúc tổng quan

```
┌───────────────────────────────────────────┐
│                 main.py                    │
│           (App – State Machine)            │
│  menu ↔ level_select ↔ playing ↔ editor   │
└──────┬────────┬────────┬──────────┬───────┘
       │        │        │          │
   ┌───▼──┐  ┌──▼──┐  ┌─▼──────┐ ┌▼────────┐
   │ ui.py│  │level│  │game.py │ │map_editor│
   │      │  │.py  │  │Session │ │  .py     │
   └──────┘  └─────┘  └───┬────┘ └─────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼────┐    ┌─────▼────┐    ┌──────▼─────┐
    │ grid.py  │    │ wave.py  │    │ tower.py   │
    │ (Map 2D) │    │ (Waves)  │    │ (Towers)   │
    └────┬─────┘    └────┬─────┘    └──────┬─────┘
         │               │                │
    ┌────▼─────┐    ┌────▼─────┐    ┌─────▼──────┐
    │ bfs.py   │    │ enemy.py │    │projectile  │
    │ ★ Queue  │    │ (Enemies)│    │  .py       │
    │ ★ BFS    │    └──────────┘    └────────────┘
    └──────────┘

    ┌──────────┐  ┌──────────────┐  ┌────────────┐
    │particle  │  │ settings.py  │  │sound_manager│
    │  .py     │  │ (Constants)  │  │  .py        │
    └──────────┘  └──────────────┘  └─────────────┘
```

---

## 📜 License

Dự án này được phát triển cho mục đích học tập trong khuôn khổ đồ án môn IT003 – Đại học Công nghệ Thông tin (UIT).

---

<p align="center">
  <b>PathFinder TD</b> – Đồ án IT003 CTDL&GT – UIT 2026<br>
  Nguyễn Minh Khang – MSSV: 25520793
</p>