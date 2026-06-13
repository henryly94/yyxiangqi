import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF

class BoardWidget(QWidget):
    move_requested = pyqtSignal(str) # Emits UCI move string like 'h2e2'

    def __init__(self, board_logic, parent=None):
        super().__init__(parent)
        self.board_logic = board_logic
        self.setMinimumSize(450, 500)
        
        # Dimensions
        self.square_size = 45
        self.margin_x = 45
        self.margin_y = 45
        
        self.selected_pos = None # (r, c)
        self.is_flipped = False
        self.edit_mode = False
        self.edit_selected_piece = 'K'
        self.setMouseTracking(True)
        
        # Piece characters mapping
        self.piece_chars = {
            'K': '帥', 'A': '仕', 'B': '相', 'N': '傌', 'R': '俥', 'C': '炮', 'P': '兵',
            'k': '將', 'a': '士', 'b': '象', 'n': '馬', 'r': '車', 'c': '砲', 'p': '卒'
        }

    def resizeEvent(self, event):
        # Calculate square size based on widget dimensions
        w = self.width()
        h = self.height()
        
        # We need 8 squares horizontally (9 lines) and 9 squares vertically (10 lines)
        self.square_size = min((w - 50) // 8, (h - 50) // 9)
        self.margin_x = (w - self.square_size * 8) / 2
        self.margin_y = (h - self.square_size * 9) / 2

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor("#f4e4c3")) # Light woody/cream color
        
        self.draw_grid(painter)
        self.draw_pieces(painter)
        
        # Draw selection highlight and legal moves ONLY if not in edit mode
        if self.selected_pos and not self.edit_mode:
            r1, c1 = self.selected_pos
            visual_r1 = 9 - r1 if self.is_flipped else r1
            visual_c1 = 8 - c1 if self.is_flipped else c1
            x = self.margin_x + visual_c1 * self.square_size
            y = self.margin_y + visual_r1 * self.square_size
            painter.setPen(QPen(QColor(0, 255, 0), 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(x - self.square_size/2, y - self.square_size/2, self.square_size, self.square_size))
            
            # Draw legal moves
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(0, 255, 0, 100))) # Semi-transparent green
            legal_moves = self.board_logic.generate_legal_moves()
            prefix = self.board_logic.pos_to_uci(r1, c1)
            for move in legal_moves:
                if move.startswith(prefix):
                    r2, c2 = self.board_logic.uci_to_pos(move[2:])
                    visual_r2 = 9 - r2 if self.is_flipped else r2
                    visual_c2 = 8 - c2 if self.is_flipped else c2
                    dx = self.margin_x + visual_c2 * self.square_size
                    dy = self.margin_y + visual_r2 * self.square_size
                    painter.drawEllipse(QRectF(dx - 5, dy - 5, 10, 10))

    def draw_grid(self, painter):
        pen = QPen(QColor("#4a3621"), 2)
        painter.setPen(pen)
        
        # Draw horizontal lines
        for r in range(10):
            y = self.margin_y + r * self.square_size
            painter.drawLine(int(self.margin_x), int(y), int(self.margin_x + 8 * self.square_size), int(y))
            
        # Draw vertical lines
        for c in range(9):
            x = self.margin_x + c * self.square_size
            # The vertical lines break at the river (between row 4 and 5)
            if c == 0 or c == 8:
                painter.drawLine(int(x), int(self.margin_y), int(x), int(self.margin_y + 9 * self.square_size))
            else:
                painter.drawLine(int(x), int(self.margin_y), int(x), int(self.margin_y + 4 * self.square_size))
                painter.drawLine(int(x), int(self.margin_y + 5 * self.square_size), int(x), int(self.margin_y + 9 * self.square_size))
                
        # Draw palaces (diagonal lines)
        # Black palace
        painter.drawLine(int(self.margin_x + 3 * self.square_size), int(self.margin_y), int(self.margin_x + 5 * self.square_size), int(self.margin_y + 2 * self.square_size))
        painter.drawLine(int(self.margin_x + 5 * self.square_size), int(self.margin_y), int(self.margin_x + 3 * self.square_size), int(self.margin_y + 2 * self.square_size))
        
        # Red palace
        painter.drawLine(int(self.margin_x + 3 * self.square_size), int(self.margin_y + 7 * self.square_size), int(self.margin_x + 5 * self.square_size), int(self.margin_y + 9 * self.square_size))
        painter.drawLine(int(self.margin_x + 5 * self.square_size), int(self.margin_y + 7 * self.square_size), int(self.margin_x + 3 * self.square_size), int(self.margin_y + 9 * self.square_size))

    def draw_pieces(self, painter):
        for r in range(10):
            for c in range(9):
                piece = self.board_logic.get_piece(r, c)
                if piece:
                    visual_r = 9 - r if self.is_flipped else r
                    visual_c = 8 - c if self.is_flipped else c
                    x = self.margin_x + visual_c * self.square_size
                    y = self.margin_y + visual_r * self.square_size
                    
                    is_red = self.board_logic.is_red(piece)
                    
                    # Draw piece background
                    painter.setPen(QPen(QColor(0, 0, 0), 1))
                    painter.setBrush(QBrush(QColor(255, 245, 230)))
                    radius = self.square_size // 2 - 2
                    painter.drawEllipse(QPointF(x, y), radius, radius)
                    
                    # Draw inner ring
                    painter.setPen(QPen(QColor(200, 180, 150), 1))
                    painter.drawEllipse(QPointF(x, y), radius - 3, radius - 3)
                    
                    # Text
                    text_color = QColor(211, 47, 47) if is_red else QColor(0, 0, 0)
                    painter.setPen(QPen(text_color))
                    font = QFont("SimHei", 20, QFont.Weight.Bold)
                    painter.setFont(font)
                    
                    name = self.piece_chars.get(piece, '?')
                    rect = QRectF(x - radius, y - radius, radius * 2, radius * 2)
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, name)

    def mousePressEvent(self, event):
        pos = event.position()
        x, y = pos.x(), pos.y()
        
        # Calculate grid coordinates
        visual_c = round((x - self.margin_x) / self.square_size)
        visual_r = round((y - self.margin_y) / self.square_size)
        
        c = 8 - visual_c if self.is_flipped else visual_c
        r = 9 - visual_r if self.is_flipped else visual_r
        
        if 0 <= c < 9 and 0 <= r < 10:
            if self.edit_mode:
                if self.edit_selected_piece == 'Eraser':
                    self.board_logic.board[r][c] = ''
                else:
                    self.board_logic.board[r][c] = self.edit_selected_piece
                self.update()
                return

            if self.selected_pos:
                # Make move
                r1, c1 = self.selected_pos
                if r1 == r and c1 == c:
                    self.selected_pos = None # Deselect
                else:
                    uci_move = self.board_logic.pos_to_uci(r1, c1) + self.board_logic.pos_to_uci(r, c)
                    self.move_requested.emit(uci_move)
                    self.selected_pos = None
            else:
                # Select piece
                piece = self.board_logic.get_piece(r, c)
                if piece:
                    # Check if it's their turn
                    is_red = self.board_logic.is_red(piece)
                    if (self.board_logic.turn == 'w' and is_red) or (self.board_logic.turn == 'b' and not is_red):
                        self.selected_pos = (r, c)
                        
            self.update()
