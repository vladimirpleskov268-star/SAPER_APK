import random
from collections import deque

class Cell:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.is_mine = False
        self.revealed = False
        self.flagged = False
        self.neighbor_mines = 0

class MinesweeperGame:
    def __init__(self, rows=9, cols=9, num_mines=10):
        self.set_board(rows, cols, num_mines)

    def set_board(self, rows, cols, num_mines):
        self.rows = max(3, min(150, rows))
        self.cols = max(3, min(150, cols))
        max_possible = self.rows * self.cols - 9
        if max_possible < 1:
            max_possible = self.rows * self.cols - 1
        self.num_mines = max(1, min(max_possible, num_mines))
        
        self.grid = [[Cell(r, c) for c in range(self.cols)] for r in range(self.rows)]
        self.first_click = True
        self.game_over = False
        self.won = False
        self.revealed_count = 0
        self.flags_placed = 0
        self.start_time = None
        self.elapsed_time = 0

    def place_mines(self, safe_r, safe_c):
        safe_zone = set()
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = safe_r + dr, safe_c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    safe_zone.add((nr, nc))
        
        all_cells = []
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) not in safe_zone:
                    all_cells.append((r, c))
        
        # If not enough non-safe cells, relax safety to just (safe_r, safe_c)
        if len(all_cells) < self.num_mines:
            all_cells = [(r, c) for r in range(self.rows) for c in range(self.cols) if (r, c) != (safe_r, safe_c)]

        mine_coords = random.sample(all_cells, min(self.num_mines, len(all_cells)))
        for r, c in mine_coords:
            self.grid[r][c].is_mine = True
            
        # Calculate numbers
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c].is_mine:
                    count = 0
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                if self.grid[nr][nc].is_mine:
                                    count += 1
                    self.grid[r][c].neighbor_mines = count

    def reveal(self, r, c):
        if self.game_over or self.won:
            return
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        
        cell = self.grid[r][c]
        if cell.flagged or cell.revealed:
            return
        
        if self.first_click:
            self.place_mines(r, c)
            self.first_click = False
            
        if cell.is_mine:
            cell.revealed = True
            self.game_over = True
            self.reveal_all_mines()
            return
            
        # BFS Flood Fill for 0 neighbor cells
        queue = deque([(r, c)])
        while queue:
            curr_r, curr_c = queue.popleft()
            curr = self.grid[curr_r][curr_c]
            if curr.revealed or curr.flagged:
                continue
            curr.revealed = True
            self.revealed_count += 1
            
            if curr.neighbor_mines == 0:
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = curr_r + dr, curr_c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            neighbor = self.grid[nr][nc]
                            if not neighbor.revealed and not neighbor.flagged:
                                queue.append((nr, nc))
                                
        self.check_win()

    def toggle_flag(self, r, c):
        if self.game_over or self.won:
            return
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        cell = self.grid[r][c]
        if cell.revealed:
            return
        cell.flagged = not cell.flagged
        if cell.flagged:
            self.flags_placed += 1
        else:
            self.flags_placed -= 1

    def chord_reveal(self, r, c):
        if self.game_over or self.won:
            return
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        cell = self.grid[r][c]
        if not cell.revealed or cell.neighbor_mines == 0:
            return
        
        flag_count = 0
        neighbors = []
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    n_cell = self.grid[nr][nc]
                    neighbors.append(n_cell)
                    if n_cell.flagged:
                        flag_count += 1
                        
        if flag_count == cell.neighbor_mines:
            for n_cell in neighbors:
                if not n_cell.flagged and not n_cell.revealed:
                    self.reveal(n_cell.r, n_cell.c)

    def reveal_all_mines(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c].is_mine:
                    self.grid[r][c].revealed = True

    def check_win(self):
        total_cells = self.rows * self.cols
        if self.revealed_count == total_cells - self.num_mines:
            self.won = True
            # Flag all remaining mines
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.grid[r][c].is_mine:
                        self.grid[r][c].flagged = True
            self.flags_placed = self.num_mines

    def remaining_mines(self):
        return self.num_mines - self.flags_placed
