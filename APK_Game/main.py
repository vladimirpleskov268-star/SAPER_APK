import sys
import time
import math
import pygame
from minesweeper import MinesweeperGame

# Initialize Pygame
pygame.init()
pygame.font.init()
try:
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except Exception:
    AUDIO_AVAILABLE = False

# Screen dimensions & mobile vertical ratio optimization
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 960
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Minesweeper Mobile 2D")

# Color Palette (Catppuccin Mocha / Sleek Dark Theme)
COLOR_BG = (24, 24, 37)          # Deep slate background
COLOR_PANEL = (30, 30, 46)       # HUD panel background
COLOR_PANEL_BORDER = (69, 71, 90) # Panel border
COLOR_CARD_UNREVEALED = (49, 50, 68) # Raised tile
COLOR_CARD_HOVER = (69, 71, 90)
COLOR_CARD_REVEALED = (17, 17, 27)   # Inset tile
COLOR_GRID_LINE = (30, 30, 46)

COLOR_TEXT_MAIN = (205, 214, 244)
COLOR_TEXT_MUTED = (166, 173, 200)

COLOR_PRIMARY = (137, 180, 250)   # Soft blue
COLOR_ACCENT = (203, 166, 247)    # Purple accent
COLOR_SUCCESS = (166, 227, 161)   # Green win
COLOR_DANGER = (243, 139, 168)    # Red loss
COLOR_FLAG = (243, 139, 168)      # Crimson flag
COLOR_MINE_BG = (235, 160, 172)   # Light red for clicked mine

# Number colors
NUMBER_COLORS = {
    1: (137, 180, 250), # Blue
    2: (166, 227, 161), # Green
    3: (243, 139, 168), # Red
    4: (203, 166, 247), # Purple
    5: (250, 179, 135), # Orange
    6: (148, 226, 213), # Teal
    7: (245, 194, 231), # Pink
    8: (186, 194, 222), # Gray
}

# Fonts
FONT_TITLE = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 24, bold=True)
FONT_HUD = pygame.font.SysFont("Consolas, Courier New, monospace", 22, bold=True)
FONT_BTN = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 16, bold=True)
FONT_MODAL = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 18)
FONT_CELL = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 20, bold=True)

# Synthetic Sound Effects
def play_beep(freq=440, duration=0.08, type='reveal'):
    if not AUDIO_AVAILABLE:
        return
    try:
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            if type == 'reveal':
                val = int(127 + 40 * math.sin(2 * math.pi * freq * t))
            elif type == 'flag':
                val = int(127 + 50 * math.sin(2 * math.pi * (freq + i * 2) * t))
            elif type == 'win':
                val = int(127 + 60 * math.sin(2 * math.pi * (freq + (i % 500)) * t))
            else: # lose
                val = int(127 + 60 * (random_val(i) % 2 - 1))
            buf.append(max(0, min(255, val)))
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(0.2)
        sound.play()
    except Exception:
        pass

def random_val(seed):
    return (seed * 1103515245 + 12345) & 0x7fffffff

class Button:
    def __init__(self, rect, text, icon="", color=COLOR_CARD_UNREVEALED, text_color=COLOR_TEXT_MAIN, active=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.icon = icon
        self.color = color
        self.text_color = text_color
        self.active = active

    def draw(self, surface):
        bg = COLOR_PRIMARY if self.active else self.color
        txt_col = (17, 17, 27) if self.active else self.text_color
        
        # Border & Rounded Box
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.rect, width=1, border_radius=8)
        
        display_str = f"{self.icon} {self.text}".strip()
        txt_surf = FONT_BTN.render(display_str, True, txt_col)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class MinesweeperApp:
    def __init__(self):
        self.game = MinesweeperGame(9, 9, 10)
        self.mode = "DIG" # DIG or FLAG
        
        # Camera & Pan/Zoom
        self.zoom = 1.0
        self.base_cell_size = 42
        self.offset_x = 0
        self.offset_y = 0
        self.is_dragging = False
        self.drag_start = (0, 0)
        self.drag_offset_start = (0, 0)
        self.touch_start_time = 0
        self.touch_start_pos = (0, 0)
        
        # Modal State
        self.show_custom_modal = False
        self.custom_rows_str = "20"
        self.custom_cols_str = "20"
        self.custom_mines_str = "60"
        self.active_input = None # 'rows', 'cols', 'mines'
        
        # Initial fit
        self.center_board()

    @property
    def cell_size(self):
        return max(14, int(self.base_cell_size * self.zoom))

    def center_board(self):
        win_w, win_h = screen.get_size()
        hud_top_h = 100
        hud_bot_h = 90
        available_h = win_h - hud_top_h - hud_bot_h
        
        # Fit zoom level automatically
        board_w = self.game.cols * self.base_cell_size
        board_h = self.game.rows * self.base_cell_size
        
        zoom_w = (win_w - 40) / max(1, board_w)
        zoom_h = (available_h - 40) / max(1, board_h)
        self.zoom = max(0.2, min(2.5, min(zoom_w, zoom_h)))
        
        actual_w = self.game.cols * self.cell_size
        actual_h = self.game.rows * self.cell_size
        
        self.offset_x = (win_w - actual_w) // 2
        self.offset_y = hud_top_h + (available_h - actual_h) // 2

    def new_game(self, rows, cols, mines):
        self.game.set_board(rows, cols, mines)
        self.center_board()

    def handle_click(self, pos, is_right_click=False, is_long_press=False):
        # Ignore clicks on HUD areas
        win_w, win_h = screen.get_size()
        hud_top_h = 100
        hud_bot_h = 90
        if pos[1] < hud_top_h or pos[1] > win_h - hud_bot_h:
            return
        
        # Calculate cell coordinates from screen position
        col = int((pos[0] - self.offset_x) // self.cell_size)
        row = int((pos[1] - self.offset_y) // self.cell_size)
        
        if 0 <= row < self.game.rows and 0 <= col < self.game.cols:
            if is_right_click or is_long_press or self.mode == "FLAG":
                self.game.toggle_flag(row, col)
                play_beep(600, 0.05, 'flag')
            else:
                cell = self.game.grid[row][col]
                if cell.revealed:
                    self.game.chord_reveal(row, col)
                    play_beep(520, 0.06, 'reveal')
                else:
                    self.game.reveal(row, col)
                    if self.game.game_over:
                        play_beep(180, 0.3, 'lose')
                    elif self.game.won:
                        play_beep(880, 0.4, 'win')
                    else:
                        play_beep(440, 0.05, 'reveal')

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            dt = clock.tick(60) / 1000.0
            win_w, win_h = screen.get_size()
            hud_top_h = 100
            hud_bot_h = 90
            
            # Start timer if first click done
            if not self.game.first_click and not self.game.game_over and not self.game.won:
                if self.game.start_time is None:
                    self.game.start_time = time.time()
                self.game.elapsed_time = int(time.time() - self.game.start_time)
            
            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.VIDEORESIZE:
                    self.center_board()
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.show_custom_modal:
                        continue
                        
                    if event.button == 1: # Left Click / Touch Start
                        self.is_dragging = True
                        self.drag_start = event.pos
                        self.drag_offset_start = (self.offset_x, self.offset_y)
                        self.touch_start_time = time.time()
                        self.touch_start_pos = event.pos
                        
                    elif event.button == 3: # Right Click
                        self.handle_click(event.pos, is_right_click=True)
                        
                    elif event.button == 4: # Mouse wheel up (Zoom In)
                        self.zoom_at(event.pos, 1.15)
                        
                    elif event.button == 5: # Mouse wheel down (Zoom Out)
                        self.zoom_at(event.pos, 0.85)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.is_dragging:
                        self.is_dragging = False
                        dx = event.pos[0] - self.drag_start[0]
                        dy = event.pos[1] - self.drag_start[1]
                        dist = math.hypot(dx, dy)
                        duration = time.time() - self.touch_start_time
                        
                        # Short tap detection (if moved less than 8px)
                        if dist < 8:
                            if duration > 0.45: # Long press -> flag
                                self.handle_click(event.pos, is_long_press=True)
                            else:
                                # Check if button clicked on top/bottom HUD
                                if not self.handle_hud_click(event.pos):
                                    self.handle_click(event.pos)
                                    
                elif event.type == pygame.MOUSEMOTION:
                    if self.is_dragging:
                        dx = event.pos[0] - self.drag_start[0]
                        dy = event.pos[1] - self.drag_start[1]
                        self.offset_x = self.drag_offset_start[0] + dx
                        self.offset_y = self.drag_offset_start[1] + dy

                elif event.type == pygame.KEYDOWN:
                    if self.show_custom_modal:
                        self.handle_modal_keydown(event)
                    else:
                        if event.key == pygame.K_r:
                            self.new_game(self.game.rows, self.game.cols, self.game.num_mines)
                        elif event.key == pygame.K_f:
                            self.mode = "FLAG" if self.mode == "DIG" else "DIG"
                        elif event.key == pygame.K_SPACE:
                            self.center_board()

            # --- Rendering ---
            screen.fill(COLOR_BG)
            self.draw_board(win_w, win_h, hud_top_h, hud_bot_h)
            self.draw_hud_top(win_w)
            self.draw_hud_bottom(win_w, win_h)
            
            if self.game.game_over or self.game.won:
                self.draw_end_game_modal(win_w, win_h)
                
            if self.show_custom_modal:
                self.draw_custom_modal(win_w, win_h)
                
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def zoom_at(self, pos, factor):
        old_zoom = self.zoom
        new_zoom = max(0.15, min(4.0, old_zoom * factor))
        if new_zoom == old_zoom:
            return
        
        # Keep mouse point centered relative to board during zoom
        mouse_x, mouse_y = pos
        rel_x = (mouse_x - self.offset_x) / (old_zoom * self.base_cell_size)
        rel_y = (mouse_y - self.offset_y) / (old_zoom * self.base_cell_size)
        
        self.zoom = new_zoom
        new_cell_size = self.cell_size
        self.offset_x = int(mouse_x - rel_x * new_cell_size)
        self.offset_y = int(mouse_y - rel_y * new_cell_size)

    def draw_board(self, win_w, win_h, hud_top_h, hud_bot_h):
        c_size = self.cell_size
        
        # Viewport Culling calculations: Only render cells visible on screen
        min_col = max(0, int((0 - self.offset_x) // c_size) - 1)
        max_col = min(self.game.cols, int((win_w - self.offset_x) // c_size) + 2)
        min_row = max(0, int((hud_top_h - self.offset_y) // c_size) - 1)
        max_row = min(self.game.rows, int((win_h - hud_bot_h - self.offset_y) // c_size) + 2)

        for r in range(min_row, max_row):
            for c in range(min_col, max_col):
                x = self.offset_x + c * c_size
                y = self.offset_y + r * c_size
                cell_rect = pygame.Rect(x, y, c_size, c_size)
                
                cell = self.game.grid[r][c]
                
                if cell.revealed:
                    if cell.is_mine:
                        pygame.draw.rect(screen, COLOR_MINE_BG, cell_rect, border_radius=4)
                        pygame.draw.circle(screen, (217, 119, 6), cell_rect.center, c_size // 3)
                        # Draw bomb emoji/icon if large enough
                        if c_size >= 18:
                            b_surf = FONT_CELL.render("💣", True, (17, 17, 27))
                            screen.blit(b_surf, b_surf.get_rect(center=cell_rect.center))
                    else:
                        pygame.draw.rect(screen, COLOR_CARD_REVEALED, cell_rect, border_radius=4)
                        pygame.draw.rect(screen, COLOR_GRID_LINE, cell_rect, width=1, border_radius=4)
                        if cell.neighbor_mines > 0:
                            num_color = NUMBER_COLORS.get(cell.neighbor_mines, COLOR_TEXT_MAIN)
                            if c_size >= 16:
                                num_font = pygame.font.SysFont("Segoe UI, Arial", max(10, int(c_size * 0.65)), bold=True)
                                txt = num_font.render(str(cell.neighbor_mines), True, num_color)
                                screen.blit(txt, txt.get_rect(center=cell_rect.center))
                else:
                    # Unrevealed tile
                    pygame.draw.rect(screen, COLOR_CARD_UNREVEALED, cell_rect, border_radius=4)
                    # Bevel light top edge
                    pygame.draw.rect(screen, (69, 71, 90), cell_rect, width=1, border_radius=4)
                    
                    if cell.flagged:
                        if c_size >= 16:
                            flag_font = pygame.font.SysFont("Segoe UI, Arial", max(10, int(c_size * 0.6)))
                            f_surf = flag_font.render("🚩", True, COLOR_FLAG)
                            screen.blit(f_surf, f_surf.get_rect(center=cell_rect.center))
                        else:
                            pygame.draw.circle(screen, COLOR_FLAG, cell_rect.center, c_size // 3)

    def draw_hud_top(self, win_w):
        hud_rect = pygame.Rect(0, 0, win_w, 100)
        pygame.draw.rect(screen, COLOR_PANEL, hud_rect)
        pygame.draw.line(screen, COLOR_PANEL_BORDER, (0, 100), (win_w, 100), 2)
        
        # Mine counter (Digital LED style)
        mines_str = f"💣 {self.game.remaining_mines():03d}"
        m_surf = FONT_HUD.render(mines_str, True, COLOR_DANGER)
        screen.blit(m_surf, (20, 20))
        
        # Timer
        time_str = f"⏱️ {self.game.elapsed_time:03d}s"
        t_surf = FONT_HUD.render(time_str, True, COLOR_PRIMARY)
        screen.blit(t_surf, (win_w - t_surf.get_width() - 20, 20))
        
        # Smiley Reset Button in middle
        face = "😊"
        if self.game.game_over:
            face = "😵"
        elif self.game.won:
            face = "😎"
            
        self.btn_reset = Button((win_w // 2 - 35, 12, 70, 42), face, color=COLOR_CARD_UNREVEALED)
        self.btn_reset.draw(screen)
        
        # Size presets buttons row
        btn_y = 60
        bw = (win_w - 40 - 20) // 5
        self.btn_easy = Button((20, btn_y, bw, 32), "9x9", color=COLOR_CARD_UNREVEALED)
        self.btn_med = Button((20 + bw + 5, btn_y, bw, 32), "16x16", color=COLOR_CARD_UNREVEALED)
        self.btn_hard = Button((20 + (bw + 5)*2, btn_y, bw, 32), "30x16", color=COLOR_CARD_UNREVEALED)
        self.btn_huge = Button((20 + (bw + 5)*3, btn_y, bw, 32), "50x50", color=COLOR_CARD_UNREVEALED)
        self.btn_custom = Button((20 + (bw + 5)*4, btn_y, bw, 32), "Custom", color=COLOR_CARD_UNREVEALED)
        
        self.btn_easy.draw(screen)
        self.btn_med.draw(screen)
        self.btn_hard.draw(screen)
        self.btn_huge.draw(screen)
        self.btn_custom.draw(screen)

    def draw_hud_bottom(self, win_w, win_h):
        hud_h = 90
        hud_rect = pygame.Rect(0, win_h - hud_h, win_w, hud_h)
        pygame.draw.rect(screen, COLOR_PANEL, hud_rect)
        pygame.draw.line(screen, COLOR_PANEL_BORDER, (0, win_h - hud_h), (win_w, win_h - hud_h), 2)
        
        btn_y = win_h - hud_h + 20
        bw = (win_w - 50) // 4
        
        # DIG / FLAG Toggle
        self.btn_dig = Button((15, btn_y, bw, 50), "DIG", icon="⛏️", active=(self.mode == "DIG"))
        self.btn_flag = Button((15 + bw + 6, btn_y, bw, 50), "FLAG", icon="🚩", active=(self.mode == "FLAG"))
        
        # Zoom + / - & Center buttons
        self.btn_zoom_in = Button((15 + (bw + 6)*2, btn_y, bw // 2 - 2, 50), "+", color=COLOR_CARD_UNREVEALED)
        self.btn_zoom_out = Button((15 + (bw + 6)*2 + bw // 2 + 2, btn_y, bw // 2 - 2, 50), "-", color=COLOR_CARD_UNREVEALED)
        self.btn_center = Button((15 + (bw + 6)*3, btn_y, bw, 50), "Center", icon="🎯", color=COLOR_CARD_UNREVEALED)
        
        self.btn_dig.draw(screen)
        self.btn_flag.draw(screen)
        self.btn_zoom_in.draw(screen)
        self.btn_zoom_out.draw(screen)
        self.btn_center.draw(screen)

    def handle_hud_click(self, pos):
        win_w, win_h = screen.get_size()
        hud_top_h = 100
        hud_bot_h = 90
        
        if pos[1] <= hud_top_h:
            if hasattr(self, 'btn_reset') and self.btn_reset.is_clicked(pos):
                self.new_game(self.game.rows, self.game.cols, self.game.num_mines)
                return True
            elif hasattr(self, 'btn_easy') and self.btn_easy.is_clicked(pos):
                self.new_game(9, 9, 10)
                return True
            elif hasattr(self, 'btn_med') and self.btn_med.is_clicked(pos):
                self.new_game(16, 16, 40)
                return True
            elif hasattr(self, 'btn_hard') and self.btn_hard.is_clicked(pos):
                self.new_game(16, 30, 99)
                return True
            elif hasattr(self, 'btn_huge') and self.btn_huge.is_clicked(pos):
                self.new_game(50, 50, 375)
                return True
            elif hasattr(self, 'btn_custom') and self.btn_custom.is_clicked(pos):
                self.show_custom_modal = True
                return True
            return True
            
        elif pos[1] >= win_h - hud_bot_h:
            if hasattr(self, 'btn_dig') and self.btn_dig.is_clicked(pos):
                self.mode = "DIG"
                return True
            elif hasattr(self, 'btn_flag') and self.btn_flag.is_clicked(pos):
                self.mode = "FLAG"
                return True
            elif hasattr(self, 'btn_zoom_in') and self.btn_zoom_in.is_clicked(pos):
                self.zoom_at((win_w // 2, win_h // 2), 1.25)
                return True
            elif hasattr(self, 'btn_zoom_out') and self.btn_zoom_out.is_clicked(pos):
                self.zoom_at((win_w // 2, win_h // 2), 0.8)
                return True
            elif hasattr(self, 'btn_center') and self.btn_center.is_clicked(pos):
                self.center_board()
                return True
            return True
            
        return False

    def draw_end_game_modal(self, win_w, win_h):
        overlay = pygame.Surface((win_w, win_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        
        modal_w, modal_h = min(400, win_w - 40), 220
        modal_rect = pygame.Rect((win_w - modal_w) // 2, (win_h - modal_h) // 2, modal_w, modal_h)
        
        pygame.draw.rect(screen, COLOR_PANEL, modal_rect, border_radius=16)
        pygame.draw.rect(screen, COLOR_PRIMARY if self.game.won else COLOR_DANGER, modal_rect, width=2, border_radius=16)
        
        title_txt = "🎉 VICTORY! 🎉" if self.game.won else "💥 GAME OVER 💥"
        title_col = COLOR_SUCCESS if self.game.won else COLOR_DANGER
        t_surf = FONT_TITLE.render(title_txt, True, title_col)
        screen.blit(t_surf, t_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 40)))
        
        sub_txt = f"Time: {self.game.elapsed_time}s  |  Board: {self.game.rows}x{self.game.cols}"
        s_surf = FONT_MODAL.render(sub_txt, True, COLOR_TEXT_MUTED)
        screen.blit(s_surf, s_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 80)))
        
        self.btn_modal_again = Button((modal_rect.centerx - 120, modal_rect.bottom - 60, 110, 42), "Play Again", color=COLOR_PRIMARY, text_color=(17,17,27))
        self.btn_modal_custom = Button((modal_rect.centerx + 10, modal_rect.bottom - 60, 110, 42), "Custom Size", color=COLOR_CARD_UNREVEALED)
        
        self.btn_modal_again.draw(screen)
        self.btn_modal_custom.draw(screen)

    def draw_custom_modal(self, win_w, win_h):
        overlay = pygame.Surface((win_w, win_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        modal_w, modal_h = min(420, win_w - 40), 320
        modal_rect = pygame.Rect((win_w - modal_w) // 2, (win_h - modal_h) // 2, modal_w, modal_h)
        
        pygame.draw.rect(screen, COLOR_PANEL, modal_rect, border_radius=16)
        pygame.draw.rect(screen, COLOR_ACCENT, modal_rect, width=2, border_radius=16)
        
        t_surf = FONT_TITLE.render("Custom Board Size (3 - 100+)", True, COLOR_TEXT_MAIN)
        screen.blit(t_surf, t_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 35)))
        
        # Inputs: Rows, Cols, Mines
        labels = ["Rows (3 - 100):", "Cols (3 - 100):", "Mines:"]
        vals = [self.custom_rows_str, self.custom_cols_str, self.custom_mines_str]
        keys = ['rows', 'cols', 'mines']
        
        self.input_rects = {}
        for i in range(3):
            y = modal_rect.top + 80 + i * 50
            lbl_surf = FONT_MODAL.render(labels[i], True, COLOR_TEXT_MUTED)
            screen.blit(lbl_surf, (modal_rect.left + 30, y + 5))
            
            box_rect = pygame.Rect(modal_rect.right - 140, y, 110, 36)
            self.input_rects[keys[i]] = box_rect
            
            is_active = (self.active_input == keys[i])
            bg = COLOR_CARD_REVEALED if is_active else COLOR_CARD_UNREVEALED
            border_col = COLOR_ACCENT if is_active else COLOR_PANEL_BORDER
            
            pygame.draw.rect(screen, bg, box_rect, border_radius=6)
            pygame.draw.rect(screen, border_col, box_rect, width=2 if is_active else 1, border_radius=6)
            
            val_surf = FONT_MODAL.render(vals[i] + ("|" if is_active else ""), True, COLOR_TEXT_MAIN)
            screen.blit(val_surf, val_surf.get_rect(center=box_rect.center))
            
        self.btn_start_custom = Button((modal_rect.centerx - 110, modal_rect.bottom - 55, 100, 40), "START", color=COLOR_SUCCESS, text_color=(17,17,27))
        self.btn_cancel_custom = Button((modal_rect.centerx + 10, modal_rect.bottom - 55, 100, 40), "CANCEL", color=COLOR_CARD_UNREVEALED)
        
        self.btn_start_custom.draw(screen)
        self.btn_cancel_custom.draw(screen)

    def handle_modal_keydown(self, event):
        if not self.active_input:
            self.active_input = 'rows'
            
        if event.key == pygame.K_RETURN:
            self.submit_custom_game()
        elif event.key == pygame.K_ESCAPE:
            self.show_custom_modal = False
        elif event.key == pygame.K_BACKSPACE:
            if self.active_input == 'rows':
                self.custom_rows_str = self.custom_rows_str[:-1]
            elif self.active_input == 'cols':
                self.custom_cols_str = self.custom_cols_str[:-1]
            elif self.active_input == 'mines':
                self.custom_mines_str = self.custom_mines_str[:-1]
        elif event.unicode.isdigit():
            if self.active_input == 'rows' and len(self.custom_rows_str) < 3:
                self.custom_rows_str += event.unicode
            elif self.active_input == 'cols' and len(self.custom_cols_str) < 3:
                self.custom_cols_str += event.unicode
            elif self.active_input == 'mines' and len(self.custom_mines_str) < 4:
                self.custom_mines_str += event.unicode

    def submit_custom_game(self):
        try:
            r = max(3, min(100, int(self.custom_rows_str or "10")))
            c = max(3, min(100, int(self.custom_cols_str or "10")))
            max_m = r * c - 9
            m = max(1, min(max_m if max_m > 0 else r*c-1, int(self.custom_mines_str or "15")))
            self.show_custom_modal = False
            self.new_game(r, c, m)
        except ValueError:
            self.show_custom_modal = False

if __name__ == "__main__":
    app = MinesweeperApp()
    app.run()
