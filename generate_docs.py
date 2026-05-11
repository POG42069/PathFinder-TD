"""
generate_docs.py - Script tự động tạo tài liệu API từ docstring
================================================================
Môn   : IT003 - Cấu trúc dữ liệu và Giải thuật
Trường: Đại học Công nghệ Thông tin (UIT)

Mô tả:
    Script này sử dụng pydoc (thư viện chuẩn Python) để tạo
    tài liệu HTML từ docstring trong code.

    Kết quả được lưu vào thư mục docs/.

Cách dùng:
    python generate_docs.py
"""

import os
import sys
import io
import pydoc
import importlib

# Fix encoding cho Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Thư mục gốc dự án
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')

# Danh sách module cần tạo tài liệu
MODULES = [
    'bfs',
    'grid',
    'tower',
    'enemy',
    'game',
    'wave',
    'projectile',
    'particle',
    'ui',
    'settings',
    'level',
    'save_manager',
    'font_manager',
    'map_editor',
    'sound_manager',
    'main',
]


def generate_docs():
    """
    Tạo tài liệu HTML cho tất cả module trong dự án.

    Quy trình:
        1. Tạo thư mục docs/ nếu chưa có
        2. Thêm thư mục dự án vào sys.path
        3. Với mỗi module:
           - Import module
           - Dùng pydoc.HTMLDoc để render HTML
           - Lưu ra file .html trong docs/
    """
    os.makedirs(DOCS_DIR, exist_ok=True)

    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)

    # Thiết lập biến môi trường để tránh pygame mở cửa sổ
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'

    success_count = 0
    fail_count = 0

    print("=" * 60)
    print("  PathFinder TD - Tạo tài liệu API (pydoc)")
    print("=" * 60)
    print(f"  Thư mục output: {DOCS_DIR}")
    print(f"  Số module: {len(MODULES)}")
    print("-" * 60)

    for module_name in MODULES:
        try:
            # Import module
            if module_name in sys.modules:
                mod = sys.modules[module_name]
                importlib.reload(mod)
            else:
                mod = importlib.import_module(module_name)

            # Tạo HTML bằng pydoc
            html_doc = pydoc.HTMLDoc()
            page_content = html_doc.page(
                pydoc.describe(mod),
                html_doc.document(mod, module_name)
            )

            # Lưu file
            output_path = os.path.join(DOCS_DIR, f'{module_name}.html')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(page_content)

            success_count += 1
            print(f"  [OK] {module_name}.html")

        except Exception as e:
            fail_count += 1
            print(f"  [FAIL] {module_name}: {e}")

    print("-" * 60)
    print(f"  Hoàn thành: {success_count}/{len(MODULES)} module")
    if fail_count > 0:
        print(f"  Thất bại: {fail_count} module")
    print(f"  Output: {DOCS_DIR}")
    print("=" * 60)

    # Tạo index.html
    _create_index(success_count)


def _create_index(total):
    """
    Tạo file index.html liệt kê tất cả module docs.

    Tham số:
        total (int): Số module đã tạo thành công.
    """
    html_parts = [
        '<!DOCTYPE html>',
        '<html lang="vi">',
        '<head>',
        '  <meta charset="utf-8">',
        '  <title>PathFinder TD - Tài liệu API</title>',
        '  <style>',
        '    body { font-family: "Segoe UI", Tahoma, sans-serif;',
        '           max-width: 800px; margin: 0 auto; padding: 20px;',
        '           background: #1a1a2e; color: #e0e0e0; }',
        '    h1 { color: #4fc3f7; text-align: center; }',
        '    h2 { color: #81c784; border-bottom: 1px solid #333; padding-bottom: 8px; }',
        '    a { color: #64b5f6; text-decoration: none; }',
        '    a:hover { color: #90caf9; text-decoration: underline; }',
        '    .module-list { list-style: none; padding: 0; }',
        '    .module-list li { padding: 8px 16px; margin: 4px 0;',
        '                      background: #16213e; border-radius: 6px;',
        '                      border-left: 3px solid #4fc3f7; }',
        '    .module-list li:hover { background: #1a2740; }',
        '    .desc { color: #90a4ae; font-size: 0.9em; margin-left: 10px; }',
        '    .info { text-align: center; color: #78909c; font-size: 0.85em;',
        '            margin-top: 30px; }',
        '  </style>',
        '</head>',
        '<body>',
        '  <h1>🏰 PathFinder TD – Tài liệu API</h1>',
        '  <p style="text-align:center; color:#78909c;">',
        '    Đồ án IT003 – CTDL&GT – UIT | Nguyễn Minh Khang – MSSV: 25520793',
        '  </p>',
        '',
        '  <h2>📦 Core Modules</h2>',
        '  <ul class="module-list">',
        '    <li><a href="bfs.html">bfs</a> <span class="desc">– Thuật toán BFS & Queue (tự implement)</span></li>',
        '    <li><a href="grid.html">grid</a> <span class="desc">– Bản đồ lưới 2D</span></li>',
        '    <li><a href="tower.html">tower</a> <span class="desc">– Các lớp tháp phòng thủ</span></li>',
        '    <li><a href="enemy.html">enemy</a> <span class="desc">– Các lớp quái vật</span></li>',
        '    <li><a href="projectile.html">projectile</a> <span class="desc">– Hệ thống đạn</span></li>',
        '    <li><a href="particle.html">particle</a> <span class="desc">– Hiệu ứng hạt</span></li>',
        '  </ul>',
        '',
        '  <h2>🎮 Game Logic</h2>',
        '  <ul class="module-list">',
        '    <li><a href="main.html">main</a> <span class="desc">– Entry point, state machine</span></li>',
        '    <li><a href="game.html">game</a> <span class="desc">– Logic game chính</span></li>',
        '    <li><a href="wave.html">wave</a> <span class="desc">– Quản lý wave</span></li>',
        '    <li><a href="level.html">level</a> <span class="desc">– Định nghĩa màn chơi</span></li>',
        '    <li><a href="settings.html">settings</a> <span class="desc">– Cấu hình toàn cục</span></li>',
        '  </ul>',
        '',
        '  <h2>🖥️ UI & Managers</h2>',
        '  <ul class="module-list">',
        '    <li><a href="ui.html">ui</a> <span class="desc">– Giao diện người dùng</span></li>',
        '    <li><a href="map_editor.html">map_editor</a> <span class="desc">– Map Editor</span></li>',
        '    <li><a href="save_manager.html">save_manager</a> <span class="desc">– Lưu dữ liệu</span></li>',
        '    <li><a href="font_manager.html">font_manager</a> <span class="desc">– Quản lý font</span></li>',
        '    <li><a href="sound_manager.html">sound_manager</a> <span class="desc">– Âm thanh</span></li>',
        '  </ul>',
        '',
        f'  <p class="info">Tạo tự động bởi pydoc | {total} module</p>',
        '</body>',
        '</html>',
    ]

    index_path = os.path.join(DOCS_DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_parts))
    print(f"  [OK] index.html (trang chính)")


if __name__ == '__main__':
    generate_docs()
