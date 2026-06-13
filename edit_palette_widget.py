from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

class EditPaletteWidget(QWidget):
    piece_selected = pyqtSignal(str) # Emits the selected piece character, or 'Eraser'

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.grid = QGridLayout()
        self.layout.addLayout(self.grid)
        
        self.selected_piece = None
        self.buttons = {}
        
        # Define pieces
        self.pieces = [
            ('K', '帅', True), ('A', '仕', True), ('B', '相', True), ('N', '马', True), ('R', '车', True), ('C', '炮', True), ('P', '兵', True),
            ('k', '将', False), ('a', '士', False), ('b', '象', False), ('n', '马', False), ('r', '车', False), ('c', '炮', False), ('p', '卒', False)
        ]
        
        # Red pieces row 0, Black pieces row 1
        for i, (char, name, is_red) in enumerate(self.pieces[:7]):
            self._add_button(char, name, is_red, 0, i)
        for i, (char, name, is_red) in enumerate(self.pieces[7:]):
            self._add_button(char, name, is_red, 1, i)
            
        # Eraser button
        self.eraser_btn = QPushButton("Eraser")
        self.eraser_btn.setFixedSize(60, 40)
        self.eraser_btn.clicked.connect(lambda: self.select_piece('Eraser'))
        self.buttons['Eraser'] = self.eraser_btn
        
        self.grid.addWidget(self.eraser_btn, 2, 0, 1, 7, Qt.AlignmentFlag.AlignCenter)
        
        self.select_piece('K') # Default selection
        
    def _add_button(self, char, name, is_red, row, col):
        btn = QPushButton(name)
        btn.setFixedSize(40, 40)
        font = QFont("SimHei", 16, QFont.Weight.Bold)
        btn.setFont(font)
        
        color = "#d32f2f" if is_red else "#000000"
        btn.setStyleSheet(f"color: {color}; background-color: #fff5e6; border: 1px solid #c8b496; border-radius: 20px;")
        
        btn.clicked.connect(lambda checked, c=char: self.select_piece(c))
        self.grid.addWidget(btn, row, col)
        self.buttons[char] = btn

    def select_piece(self, piece_char):
        self.selected_piece = piece_char
        
        # Reset styles
        for char, btn in self.buttons.items():
            if char == 'Eraser':
                if char == piece_char:
                    btn.setStyleSheet("background-color: #d1e7dd; border: 2px solid #0f5132; font-weight: bold;")
                else:
                    btn.setStyleSheet("")
            else:
                is_red = char.isupper()
                color = "#d32f2f" if is_red else "#000000"
                if char == piece_char:
                    btn.setStyleSheet(f"color: {color}; background-color: #d1e7dd; border: 3px solid #0f5132; border-radius: 20px;")
                else:
                    btn.setStyleSheet(f"color: {color}; background-color: #fff5e6; border: 1px solid #c8b496; border-radius: 20px;")
                    
        self.piece_selected.emit(piece_char)
