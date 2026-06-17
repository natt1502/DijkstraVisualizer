import tkinter as tk
from tkinter import messagebox
import networkx as nx
import random
import math

# ================================================
# CẤU HÌNH MÀU SẮC
# ================================================
BG_CANVAS  = "#1e1e2e"
CLR_NORMAL = "#3a3a5c"
CLR_PATH   = "#d13438"
CLR_START  = "#107c10"
CLR_END    = "#7b2d8b"
CLR_EDGE   = "#555577"
CLR_PATH_E = "#ff6b6b"
R = 20


class DijkstraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dijkstra Visualizer — Mạng Router Doanh Nghiệp")
        self.root.configure(bg="#f0f0f0")
        self.root.geometry("900x560")

        self.G     = nx.Graph()
        self.pos   = {}
        self.start = None
        self.end   = None
        self.mode  = None   # "set_start" hoặc "set_end"

        self._build_ui()
        self._load_bai2()   # load đồ thị bài 2 mặc định

    # ================================================
    # BƯỚC 1: Xây dựng giao diện
    # ================================================
    def _build_ui(self):
        # ---------- Sidebar ----------
        sidebar = tk.Frame(self.root, bg="#e8e8e8", width=190, padx=8, pady=8)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="DIJKSTRA VISUALIZER",
                 bg="#e8e8e8", fg="#0078d4",
                 font=("Arial", 10, "bold")).pack(pady=(4, 8))

        # --- Nhóm: Chọn đồ thị ---
        tk.Label(sidebar, text="① Chọn đồ thị",
                 bg="#e8e8e8", font=("Arial", 9, "bold")).pack(anchor="w")

        tk.Button(sidebar, text="Đồ thị mẫu Bài 2",
                  command=self._load_bai2, width=22,
                  bg="#0078d4", fg="white",
                  font=("Arial", 9, "bold")).pack(pady=2)

        tk.Button(sidebar, text="Sinh ngẫu nhiên (15 node)",
                  command=self._gen_graph, width=22,
                  bg="#005a9e", fg="white").pack(pady=2)

        tk.Frame(sidebar, bg="#cccccc", height=1).pack(fill="x", pady=6)

        # --- Nhóm: Chọn điểm ---
        tk.Label(sidebar, text="② Chọn điểm (click chuột)",
                 bg="#e8e8e8", font=("Arial", 9, "bold")).pack(anchor="w")

        tk.Button(sidebar, text="[1] Chọn điểm BẮT ĐẦU",
                  command=lambda: self._set_mode("set_start"),
                  bg="#107c10", fg="white", width=22).pack(pady=2)

        tk.Button(sidebar, text="[2] Chọn điểm KẾT THÚC",
                  command=lambda: self._set_mode("set_end"),
                  bg="#7b2d8b", fg="white", width=22).pack(pady=2)

        # Nhãn hiển thị node đã chọn
        self.lbl_start = tk.Label(sidebar, text="Bắt đầu: chưa chọn",
                                  bg="#e8e8e8", fg="#107c10",
                                  font=("Arial", 8))
        self.lbl_start.pack(anchor="w", padx=4)

        self.lbl_end = tk.Label(sidebar, text="Kết thúc: chưa chọn",
                                bg="#e8e8e8", fg="#7b2d8b",
                                font=("Arial", 8))
        self.lbl_end.pack(anchor="w", padx=4)

        tk.Frame(sidebar, bg="#cccccc", height=1).pack(fill="x", pady=6)

        # --- Nhóm: Chạy ---
        tk.Label(sidebar, text="③ Chạy thuật toán",
                 bg="#e8e8e8", font=("Arial", 9, "bold")).pack(anchor="w")

        tk.Button(sidebar, text="▶  Chạy Dijkstra",
                  command=self._run_dijkstra,
                  bg="#d13438", fg="white", width=22,
                  font=("Arial", 10, "bold")).pack(pady=4)

        tk.Button(sidebar, text="✕  Reset",
                  command=self._reset,
                  bg="#555555", fg="white", width=22).pack(pady=2)

        tk.Frame(sidebar, bg="#cccccc", height=1).pack(fill="x", pady=6)

        # --- Kết quả ---
        tk.Label(sidebar, text="Kết quả:",
                 bg="#e8e8e8", font=("Arial", 9, "bold")).pack(anchor="w")

        self.result_text = tk.Text(sidebar, height=7, width=23,
                                   font=("Arial", 8), state="disabled",
                                   bg="#ffffff", relief="sunken", wrap="word")
        self.result_text.pack(pady=2)

        # Nhãn trạng thái dưới cùng
        self.status_var = tk.StringVar(value="")
        tk.Label(sidebar, textvariable=self.status_var,
                 bg="#e8e8e8", fg="#555555",
                 font=("Arial", 8), wraplength=175,
                 justify="left").pack(anchor="w", padx=4)

        # ---------- Canvas ----------
        self.canvas = tk.Canvas(self.root, bg=BG_CANVAS,
                                width=710, height=560)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Bắt sự kiện click chuột
        self.canvas.bind("<Button-1>", self._on_canvas_click)

    # ================================================
    # BƯỚC 2: Hiển thị dòng nhắc trên canvas
    # ================================================
    def _show_hint(self, message, color="#FFD700"):
        # Xóa hint cũ
        self.canvas.delete("hint")

        # Nền mờ phía sau chữ
        self.canvas.create_rectangle(
            8, 8, 692, 36,
            fill="#000000", stipple="gray50",
            outline="", tags="hint"
        )
        # Chữ hướng dẫn
        self.canvas.create_text(
            16, 22,
            text=message,
            fill=color, anchor="w",
            font=("Arial", 10, "bold"),
            tags="hint"
        )

    # ================================================
    # BƯỚC 3: Chế độ chọn node + nhắc người dùng
    # ================================================
    def _set_mode(self, mode):
        self.mode = mode
        if mode == "set_start":
            self._show_hint(
                "👆 Hãy click vào node trên canvas để chọn điểm BẮT ĐẦU",
                color="#6fcf6f"
            )
            self.status_var.set("Đang chờ click chọn điểm bắt đầu...")
        elif mode == "set_end":
            self._show_hint(
                "👆 Hãy click vào node trên canvas để chọn điểm KẾT THÚC",
                color="#c77dca"
            )
            self.status_var.set("Đang chờ click chọn điểm kết thúc...")

    # ================================================
    # BƯỚC 4: Xử lý click chuột trên canvas
    # ================================================
    def _on_canvas_click(self, event):
        if self.mode is None:
            # Nếu chưa nhấn nút chọn, nhắc người dùng
            self._show_hint(
                "⚠  Nhấn nút [1] hoặc [2] ở bên trái trước khi click chọn node!",
                color="#FF6B6B"
            )
            return

        # Tìm node gần nhất với vị trí click
        clicked = None
        for node, (x, y) in self.pos.items():
            if abs(event.x - x) <= R and abs(event.y - y) <= R:
                clicked = node
                break

        # Click vào vùng trống
        if clicked is None:
            self._show_hint(
                "⚠  Không trúng node! Hãy click thẳng vào hình tròn của router.",
                color="#FF6B6B"
            )
            return

        # Xử lý theo chế độ
        if self.mode == "set_start":
            self.start = clicked
            self.lbl_start.config(text=f"Bắt đầu: {clicked}")
            self.status_var.set(f"Đã chọn bắt đầu: {clicked}")

            self._draw_graph()   # vẽ lại trước

            # Nhắc bước tiếp theo
            if self.end is None:
                self._show_hint(
                    f"✔  Đã chọn điểm bắt đầu: {clicked}  →  Tiếp theo nhấn nút [2] chọn điểm KẾT THÚC",
                    color="#6fcf6f"
                )
            else:
                self._show_hint(
                    f"✔  {self.start}  →  {self.end}  |  Nhấn ▶ Chạy Dijkstra để tìm đường!",
                    color="#FFD700"
                )

        elif self.mode == "set_end":
            self.end = clicked
            self.lbl_end.config(text=f"Kết thúc:  {clicked}")
            self.status_var.set(f"Đã chọn kết thúc: {clicked}")

            self._draw_graph()   # vẽ lại trước

            if self.start is None:
                self._show_hint(
                    f"✔  Đã chọn điểm kết thúc: {clicked}  →  Tiếp theo nhấn nút [1] chọn điểm BẮT ĐẦU",
                    color="#c77dca"
                )
            else:
                self._show_hint(
                    f"✔  {self.start}  →  {self.end}  |  Nhấn ▶ Chạy Dijkstra để tìm đường!",
                    color="#FFD700"
                )

        self.mode = None   # thoát chế độ chọn

    # ================================================
    # BƯỚC 5: Sinh đồ thị ngẫu nhiên
    # ================================================
    def _gen_graph(self):
        self.G.clear()
        self.pos.clear()
        self.start = self.end = None
        self.lbl_start.config(text="Bắt đầu: chưa chọn")
        self.lbl_end.config(text="Kết thúc: chưa chọn")

        nodes = [f"R{i}" for i in range(15)]
        self.G.add_nodes_from(nodes)

        # Vị trí node theo hình tròn + nhiễu ngẫu nhiên
        W, H = 680, 500
        cx, cy = W // 2, H // 2 + 20
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / 15
            rx = random.randint(150, 220)
            ry = random.randint(120, 180)
            x = int(cx + rx * math.cos(angle))
            y = int(cy + ry * math.sin(angle))
            self.pos[node] = (x, y)

        # Sinh cạnh ngẫu nhiên
        for i, node in enumerate(nodes):
            neighbors = random.sample(
                [n for n in nodes if n != node],
                k=random.randint(2, 4)
            )
            for nb in neighbors:
                if not self.G.has_edge(node, nb):
                    self.G.add_edge(node, nb, weight=random.randint(3, 20))

        # Đảm bảo đồ thị liên thông
        comps = list(nx.connected_components(self.G))
        for i in range(1, len(comps)):
            u = random.choice(list(comps[0]))
            v = random.choice(list(comps[i]))
            self.G.add_edge(u, v, weight=random.randint(5, 15))

        self._draw_graph()
        self._show_hint(
            "✔  Đã sinh đồ thị ngẫu nhiên!  →  Nhấn [1] để chọn điểm BẮT ĐẦU",
            color="#6fcf6f"
        )
        self.status_var.set("Đồ thị ngẫu nhiên sẵn sàng.")

    # ================================================
    # BƯỚC 6: Load đồ thị mẫu bài 2
    # ================================================
    def _load_bai2(self):
        self.G.clear()
        self.start = self.end = None
        self.lbl_start.config(text="Bắt đầu: chưa chọn")
        self.lbl_end.config(text="Kết thúc: chưa chọn")

        edges = [
            ("R0","R1",5), ("R0","R2",10), ("R1","R3",3),
            ("R1","R4",8), ("R2","R4",6),  ("R2","R5",12),
            ("R3","R6",4), ("R4","R6",7),  ("R4","R7",9),
            ("R5","R7",5), ("R5","R8",11), ("R6","R9",6),
            ("R7","R9",4), ("R7","R10",8), ("R8","R10",3),
            ("R8","R11",7),("R9","R12",5), ("R10","R12",9),
            ("R10","R13",6),("R11","R13",4),("R12","R14",3),
            ("R13","R14",5),("R3","R5",15),("R6","R11",10),
        ]
        self.pos = {
            "R0": (80,  80),  "R1": (220, 80),  "R2": (80,  180),
            "R3": (220, 180), "R4": (340, 180),  "R5": (80,  280),
            "R6": (460, 180), "R7": (460, 280),  "R8": (80,  380),
            "R9": (560, 280), "R10":(560, 380),  "R11":(340, 380),
            "R12":(630, 200), "R13":(630, 380),  "R14":(630, 460),
        }
        for u, v, w in edges:
            self.G.add_edge(u, v, weight=w)

        self._draw_graph()
        self._show_hint(
            "✔  Đã load đồ thị Bài 2!  →  Nhấn [1] để chọn điểm BẮT ĐẦU",
            color="#6fcf6f"
        )
        self.status_var.set("Đồ thị Bài 2 sẵn sàng.")

    # ================================================
    # BƯỚC 7: Vẽ đồ thị lên canvas
    # ================================================
    def _draw_graph(self, path_edges=None, path_nodes=None):
        self.canvas.delete("all")
        path_edges = path_edges or set()
        path_nodes = path_nodes or set()

        # Vẽ cạnh
        for u, v, data in self.G.edges(data=True):
            x1, y1 = self.pos[u]
            x2, y2 = self.pos[v]

            is_path = (u, v) in path_edges or (v, u) in path_edges
            color = CLR_PATH_E if is_path else CLR_EDGE
            width = 3 if is_path else 1

            self.canvas.create_line(x1, y1, x2, y2,
                                    fill=color, width=width)

            # Nhãn trọng số giữa cạnh
            mx = (x1 + x2) // 2
            my = (y1 + y2) // 2
            self.canvas.create_text(mx, my - 8,
                                    text=str(data["weight"]),
                                    fill="#aaaaaa",
                                    font=("Arial", 7))

        # Vẽ node
        for node, (x, y) in self.pos.items():
            if node == self.start:
                color = CLR_START
            elif node == self.end:
                color = CLR_END
            elif node in path_nodes:
                color = CLR_PATH
            else:
                color = CLR_NORMAL

            self.canvas.create_oval(
                x - R, y - R, x + R, y + R,
                fill=color, outline="white", width=1.5
            )
            self.canvas.create_text(x, y, text=node,
                                    fill="white",
                                    font=("Arial", 8, "bold"))

        # Vẽ chú thích màu
        self._draw_legend()

    # ================================================
    # BƯỚC 8: Vẽ chú thích màu
    # ================================================
    def _draw_legend(self):
        items = [
            (CLR_START, "Nguồn"),
            (CLR_END,   "Đích"),
            (CLR_PATH,  "Đường đi"),
            (CLR_NORMAL,"Router thường"),
        ]
        x, y = 10, 510
        for color, label in items:
            self.canvas.create_oval(x, y, x + 12, y + 12,
                                    fill=color, outline="white")
            self.canvas.create_text(x + 16, y + 6,
                                    text=label, fill="#cccccc",
                                    font=("Arial", 8), anchor="w")
            x += 105

    # ================================================
    # BƯỚC 9: Chạy Dijkstra
    # ================================================
    def _run_dijkstra(self):
        # Chưa chọn điểm bắt đầu
        if not self.start:
            self._show_hint(
                "⚠  Chưa chọn điểm bắt đầu!  →  Nhấn nút [1] rồi click vào node",
                color="#FF6B6B"
            )
            self.status_var.set("Hãy chọn điểm bắt đầu trước.")
            return

        # Chưa chọn điểm kết thúc
        if not self.end:
            self._show_hint(
                "⚠  Chưa chọn điểm kết thúc!  →  Nhấn nút [2] rồi click vào node",
                color="#FF6B6B"
            )
            self.status_var.set("Hãy chọn điểm kết thúc trước.")
            return

        # Trùng điểm
        if self.start == self.end:
            self._show_hint(
                "⚠  Điểm bắt đầu và kết thúc trùng nhau! Hãy chọn lại.",
                color="#FF6B6B"
            )
            return

        # Chạy Dijkstra
        try:
            path = nx.dijkstra_path(
                self.G, self.start, self.end, weight="weight"
            )
            cost = nx.dijkstra_path_length(
                self.G, self.start, self.end, weight="weight"
            )
        except nx.NetworkXNoPath:
            self._show_hint(
                "⚠  Không tìm được đường đi giữa hai node này!",
                color="#FF6B6B"
            )
            messagebox.showerror("Lỗi", "Không tìm được đường đi!")
            return

        # Tập hợp cạnh và node trên đường đi
        path_edges = set(zip(path, path[1:]))
        path_nodes = set(path)

        # Vẽ lại với màu đường đi
        self._draw_graph(path_edges, path_nodes)

        # Hiện hint thành công
        self._show_hint(
            f"✔  Tìm thấy!  {' → '.join(path)}  |  Tổng: {cost} ms",
            color="#FFD700"
        )

        # Hiện kết quả vào hộp text
        result = (
            f"Đường đi:\n"
            f"{' → '.join(path)}\n\n"
            f"Tổng độ trễ: {cost} ms\n"
            f"Số bước: {len(path) - 1} hop\n"
            f"Số node: {len(path)}"
        )
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", result)
        self.result_text.config(state="disabled")

        self.status_var.set(f"Hoàn thành! Độ trễ: {cost} ms")

    # ================================================
    # BƯỚC 10: Reset
    # ================================================
    def _reset(self):
        self.start = self.end = self.mode = None
        self.lbl_start.config(text="Bắt đầu: chưa chọn")
        self.lbl_end.config(text="Kết thúc:  chưa chọn")

        self._draw_graph()

        self._show_hint(
            "✔  Đã reset!  →  Nhấn [1] để chọn lại điểm BẮT ĐẦU",
            color="#6fcf6f"
        )

        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state="disabled")

        self.status_var.set("Đã reset xong.")


# ================================================
# CHẠY ỨNG DỤNG
# ================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = DijkstraApp(root)
    root.mainloop()
