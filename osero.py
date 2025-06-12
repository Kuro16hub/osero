import tkinter as tk

BOARD_SIZE = 8
CELL_SIZE = 50
EMPTY, BLACK, WHITE = 0, 1, 2
DIRECTIONS = [(0,1),(1,0),(0,-1),(-1,0),(1,1),(-1,-1),(1,-1),(-1,1)]

class OthelloGUI:
    def __init__(self, root):
        self.root = root
        self.canvas_size = BOARD_SIZE * CELL_SIZE
        self.root.title("オセロ")
        self.game_over = False
        self.pass_count = 0

        # 上部：ラベル + スコア
        self.top_frame = tk.Frame(root)
        self.top_frame.pack()
        self.turn_label = tk.Label(self.top_frame, text="黒の番です", font=("Arial",14), fg="black")
        self.turn_label.pack(side="left", padx=20)
        self.score_label = tk.Label(self.top_frame, text="黒: 2  白: 2", font=("Arial",14))
        self.score_label.pack(side="left", padx=20)

        # 盤面
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg="green")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.board = [[EMPTY]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_player = BLACK
        self.initialize_board()
        self.draw_board()

    def initialize_board(self):
        mid = BOARD_SIZE // 2
        self.board[mid-1][mid-1] = WHITE
        self.board[mid][mid] = WHITE
        self.board[mid-1][mid] = BLACK
        self.board[mid][mid-1] = BLACK

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x1, y1 = c*CELL_SIZE, r*CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")
                if self.board[r][c] == BLACK:
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="black")
                elif self.board[r][c] == WHITE:
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="white")
        self.show_valid_moves()
        self.update_score()

    def show_valid_moves(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.is_valid_move(r, c):
                    cx = c * CELL_SIZE + CELL_SIZE // 2
                    cy = r * CELL_SIZE + CELL_SIZE // 2
                    self.canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="red")

    def is_valid_move(self, r, c):
        if self.board[r][c] != EMPTY: return False
        opp = WHITE if self.current_player == BLACK else BLACK
        for dr, dc in DIRECTIONS:
            rr, cc = r+dr, c+dc
            found = False
            while 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE:
                if self.board[rr][cc] == opp:
                    found = True
                elif self.board[rr][cc] == self.current_player:
                    if found: return True
                    break
                else: break
                rr += dr
                cc += dc
        return False

    def place_piece(self, r, c):
        if not self.is_valid_move(r, c): return False
        self.board[r][c] = self.current_player
        opp = WHITE if self.current_player == BLACK else BLACK
        for dr, dc in DIRECTIONS:
            rr, cc = r+dr, c+dc
            path = []
            while 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE:
                if self.board[rr][cc] == opp:
                    path.append((rr, cc))
                elif self.board[rr][cc] == self.current_player:
                    for pr, pc in path:
                        self.board[pr][pc] = self.current_player
                    break
                else: break
                rr += dr
                cc += dc
        return True

    def has_valid_moves(self, player):
        saved = self.current_player
        self.current_player = player
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.is_valid_move(r, c):
                    self.current_player = saved
                    return True
        self.current_player = saved
        return False

    def update_score(self):
        black = sum(row.count(BLACK) for row in self.board)
        white = sum(row.count(WHITE) for row in self.board)
        self.score_label.config(text=f"黒: {black}  白: {white}")
        if black + white == 64 and not self.game_over:
            self.show_winner()

    def switch_player(self):
        self.current_player = BLACK if self.current_player == WHITE else WHITE
        self.turn_label.config(text="黒の番です" if self.current_player == BLACK else "白の番です", fg="black")
        if self.has_valid_moves(self.current_player):
            self.pass_count = 0
        else:
            self.pass_count += 1
            if self.pass_count >= 2:
                self.show_winner()
            else:
                self.switch_player()

    def show_winner(self):
        black = sum(row.count(BLACK) for row in self.board)
        white = sum(row.count(WHITE) for row in self.board)
        if black > white:
            result = "WINNER: 黒"
        elif white > black:
            result = "WINNER: 白"
        else:
            result = "DRAW"
        self.game_over = True

        # 勝者を上部ラベルに表示（番ラベルを上書き）
        self.turn_label.config(text=result, fg="red")

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)
        tk.Button(self.button_frame, text="もう一度プレイ", font=("Arial", 12),
                  command=self.reset_game).pack(side="left", padx=10)
        tk.Button(self.button_frame, text="終了", font=("Arial", 12),
                  command=self.root.quit).pack(side="left", padx=10)

    def reset_game(self):
        self.board = [[EMPTY]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_player = BLACK
        self.pass_count = 0
        self.game_over = False
        self.initialize_board()
        self.turn_label.config(text="黒の番です", fg="black")
        self.score_label.config(text="黒: 2  白: 2")
        if hasattr(self, "button_frame"):
            self.button_frame.destroy()
        self.draw_board()

    def on_click(self, event):
        if self.game_over: return
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            if self.place_piece(row, col):
                self.switch_player()
                self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    game = OthelloGUI(root)
    root.mainloop()