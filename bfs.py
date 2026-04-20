"""
bfs.py - Thuật toán BFS và cấu trúc dữ liệu Queue (tự implement)
=========================================================
Môn   : IT003 - Cấu trúc dữ liệu và Giải thuật
Trường: Đại học Công nghệ Thông tin (UIT)

Mô tả:
    Module này tự implement cấu trúc dữ liệu Queue (Hàng đợi) và
    thuật toán BFS (Breadth-First Search – Tìm kiếm theo chiều rộng)
    mà KHÔNG sử dụng bất kỳ thư viện ngoài nào.

    BFS được dùng để tìm đường ngắn nhất cho quái vật di chuyển
    từ điểm xuất hiện (spawn) đến căn cứ (base) trên bản đồ lưới 2D.
"""



class Queue:
    """
    Cấu trúc dữ liệu Hàng đợi (Queue) – tự implement bằng Python list.

    Nguyên tắc hoạt động: FIFO (First In – First Out)
        Phần tử được thêm vào cuối (enqueue) và
        lấy ra từ đầu (dequeue).

    Ứng dụng trong BFS:
        BFS cần duyệt các đỉnh theo thứ tự "gần trước – xa sau",
        đúng với nguyên tắc FIFO của Queue.

    Độ phức tạp:
        enqueue : O(1) – thêm vào cuối danh sách
        dequeue : O(n) – pop(0) phải dịch chuyển toàn bộ mảng
        peek    : O(1)
        is_empty: O(1)
    """

    def __init__(self):
        """Khởi tạo hàng đợi rỗng."""
        self._data = []


    def enqueue(self, item):
        """
        Thêm phần tử vào cuối hàng đợi.

        Tham số:
            item: Phần tử cần thêm (bất kỳ kiểu dữ liệu nào).
        """
        self._data.append(item)

    def dequeue(self):
        """
        Lấy và xóa phần tử ở đầu hàng đợi.

        Trả về:
            Phần tử đầu tiên trong hàng đợi.

        Ngoại lệ:
            IndexError: Nếu hàng đợi rỗng.
        """
        if self.is_empty():
            raise IndexError("dequeue() gọi trên hàng đợi rỗng")
        return self._data.pop(0)

    def peek(self):
        """
        Xem phần tử đầu hàng đợi mà không xóa.

        Trả về:
            Phần tử đầu tiên, hoặc None nếu hàng đợi rỗng.
        """
        if self.is_empty():
            return None
        return self._data[0]

    def is_empty(self):
        """
        Kiểm tra hàng đợi có rỗng không.

        Trả về:
            bool: True nếu rỗng, False nếu còn phần tử.
        """
        return len(self._data) == 0

    def size(self):
        """
        Số lượng phần tử hiện có trong hàng đợi.

        Trả về:
            int: Số phần tử.
        """
        return len(self._data)

    def clear(self):
        """Xóa toàn bộ phần tử trong hàng đợi."""
        self._data = []

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"Queue({self._data})"



def bfs(grid_data, start, end, rows, cols):
    """
    Thuật toán BFS (Breadth-First Search) – Tìm kiếm theo chiều rộng.

    Mục đích:
        Tìm đường đi ngắn nhất (theo số bước) từ ô `start` đến ô `end`
        trên bản đồ lưới 2D, tránh các ô bị chặn.

    Nguyên lý hoạt động:
        1. Đưa ô bắt đầu vào hàng đợi (Queue).
        2. Lặp: lấy ô từ đầu hàng đợi, kiểm tra 4 hướng lân cận.
        3. Với mỗi ô lân cận hợp lệ (chưa thăm, không bị chặn):
           – Đánh dấu đã thăm
           – Ghi nhận ô cha (để truy vết đường đi)
           – Đưa vào hàng đợi
        4. Nếu tìm đến ô đích → truy vết ngược lại để lấy path.
        5. Nếu hàng đợi rỗng mà chưa đến đích → không có đường.

    Tham số:
        grid_data (list[list[int]]):
            Ma trận trạng thái ô lưới. Giá trị:
              0 (CELL_EMPTY)    – đi được, xây tháp được
              1 (CELL_BLOCKED)  – bị tháp chặn, BFS không qua
              2 (CELL_SPAWN)    – điểm xuất phát, BFS bắt đầu
              3 (CELL_BASE)     – căn cứ, điểm đích BFS
              4 (CELL_OBSTACLE) – địa hình cố định, không đi được
        start (tuple[int, int]):
            Tọa độ (row, col) của ô xuất phát.
        end (tuple[int, int]):
            Tọa độ (row, col) của ô đích.
        rows (int): Tổng số hàng của lưới.
        cols (int): Tổng số cột của lưới.

    Trả về:
        list[tuple[int, int]]:
            Danh sách tọa độ (row, col) tạo thành đường đi ngắn nhất
            từ `start` đến `end`, bao gồm cả 2 điểm đầu cuối.
            Trả về danh sách rỗng [] nếu không tìm thấy đường.

    Độ phức tạp:
        Thời gian : O(V + E) = O(rows × cols)  – mỗi ô thăm tối đa 1 lần
        Không gian: O(rows × cols)              – lưu trạng thái visited & parent

    Ví dụ:
        >>> grid = [[0,0,0],[0,1,0],[0,0,0]]
        >>> bfs(grid, (0,0), (2,2), 3, 3)
        [(0,0), (1,0), (2,0), (2,1), (2,2)]
    """

    if start == end:
        return [start]

    DIRECTIONS = [
        (-1,  0),
        ( 1,  0),
        ( 0, -1),
        ( 0,  1),
    ]


    queue = Queue()
    queue.enqueue(start)

    visited = set()
    visited.add(start)

    parent = {start: None}


    while not queue.is_empty():

        current = queue.dequeue()

        if current == end:
            path = []
            node = end
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            return path

        row, col = current

        import random
        dirs = list(DIRECTIONS)
        random.shuffle(dirs)

        for dr, dc in dirs:
            nr, nc = row + dr, col + dc
            neighbor = (nr, nc)

            in_bounds  = 0 <= nr < rows and 0 <= nc < cols
            not_visited = neighbor not in visited
            cell_val = grid_data[nr][nc] if in_bounds else -1
            passable  = cell_val in (0, 2, 3)

            if in_bounds and not_visited and passable:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.enqueue(neighbor)

    return []



def has_path(grid_data, start, end, rows, cols):
    """
    Kiểm tra nhanh xem có tồn tại đường đi từ start đến end không.

    Trả về:
        bool: True nếu có đường đi hợp lệ.
    """
    return len(bfs(grid_data, start, end, rows, cols)) > 0
