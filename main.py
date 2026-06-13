import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QListWidget, 
                             QFileDialog, QLabel, QSplitter, QListWidgetItem,
                             QInputDialog, QMessageBox, QComboBox)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

from xiangqi_logic import Board
from board_widget import BoardWidget
from engine_client import EngineClient
from edit_palette_widget import EditPaletteWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xiangqi GUI")
        self.resize(900, 700)
        
        self.board_logic = Board()
        self.engine = None
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left side: Board
        self.board_widget = BoardWidget(self.board_logic)
        self.board_widget.move_requested.connect(self.handle_user_move)
        
        # Right side: Controls and Info
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.btn_load_engine = QPushButton("Load Engine")
        self.btn_start_analysis = QPushButton("Start Analysis")
        self.btn_stop_analysis = QPushButton("Stop Analysis")
        self.btn_start_analysis.setEnabled(False)
        self.btn_stop_analysis.setEnabled(False)
        
        self.btn_load_engine.clicked.connect(self.load_engine)
        self.btn_start_analysis.clicked.connect(self.start_analysis)
        
        controls_layout.addWidget(self.btn_load_engine)
        controls_layout.addWidget(self.btn_start_analysis)
        controls_layout.addWidget(self.btn_stop_analysis)
        
        # Game controls
        game_controls_layout = QHBoxLayout()
        self.btn_new_game = QPushButton("New Game")
        self.btn_load_pgn = QPushButton("Load PGN")
        self.btn_save_pgn = QPushButton("Save PGN")
        
        self.btn_start_analysis.clicked.connect(self.start_analysis_request)
        self.btn_stop_analysis.clicked.connect(self.stop_analysis)
        self.btn_load_pgn.clicked.connect(self.load_pgn)
        self.btn_save_pgn.clicked.connect(self.save_pgn)
        self.btn_new_game.clicked.connect(self.new_game)
        
        game_controls_layout.addWidget(self.btn_new_game)
        game_controls_layout.addWidget(self.btn_load_pgn)
        game_controls_layout.addWidget(self.btn_save_pgn)
        
        # Additional controls
        extra_controls_layout = QHBoxLayout()
        self.btn_flip_board = QPushButton("Flip Board")
        self.btn_set_fen = QPushButton("Set FEN")
        self.btn_edit_mode = QPushButton("Enter Edit Mode")
        
        self.btn_flip_board.clicked.connect(self.flip_board)
        self.btn_set_fen.clicked.connect(self.set_fen_dialog)
        self.btn_edit_mode.clicked.connect(self.toggle_edit_mode)
        
        extra_controls_layout.addWidget(self.btn_flip_board)
        extra_controls_layout.addWidget(self.btn_set_fen)
        extra_controls_layout.addWidget(self.btn_edit_mode)
        
        # Edit Mode Panel (Hidden by default)
        self.edit_panel = QWidget()
        edit_layout = QVBoxLayout(self.edit_panel)
        
        self.edit_palette = EditPaletteWidget()
        self.edit_palette.piece_selected.connect(self.on_palette_piece_selected)
        
        edit_controls = QHBoxLayout()
        self.btn_clear_board = QPushButton("Clear Board")
        self.btn_clear_board.clicked.connect(self.clear_board)
        
        self.turn_combo = QComboBox()
        self.turn_combo.addItems(["Red to Move", "Black to Move"])
        
        edit_controls.addWidget(self.btn_clear_board)
        edit_controls.addWidget(self.turn_combo)
        
        edit_layout.addWidget(QLabel("<b>Board Editor</b>"))
        edit_layout.addWidget(self.edit_palette)
        edit_layout.addLayout(edit_controls)
        
        self.edit_panel.setVisible(False)
        
        # Navigation
        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("< Prev")
        self.btn_next = QPushButton("Next >")
        self.btn_prev.clicked.connect(self.prev_move)
        self.btn_next.clicked.connect(self.next_move)
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.btn_next)
        
        # Move History
        self.move_list = QListWidget()
        
        # Engine Output
        self.engine_score_label = QLabel("Score: N/A")
        self.engine_score_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        self.engine_pv_label = QLabel("Recommended Line: N/A")
        self.engine_pv_label.setWordWrap(True)
        self.engine_pv_label.setStyleSheet("color: #d32f2f; font-weight: bold; padding: 5px; border: 1px solid #ccc;")
        
        self.engine_log = QTextEdit()
        self.engine_log.setReadOnly(True)
        
        right_layout.addLayout(controls_layout)
        right_layout.addLayout(game_controls_layout)
        right_layout.addLayout(extra_controls_layout)
        right_layout.addWidget(self.edit_panel)
        right_layout.addLayout(nav_layout)
        right_layout.addWidget(QLabel("Move History:"))
        right_layout.addWidget(self.move_list)
        right_layout.addWidget(QLabel("Engine Analysis:"))
        right_layout.addWidget(self.engine_score_label)
        right_layout.addWidget(self.engine_pv_label)
        right_layout.addWidget(self.engine_log)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.board_widget)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 300])
        
        main_layout.addWidget(splitter)
        
    def handle_user_move(self, uci_move):
        # We try to make the move
        success = self.board_logic.make_move_uci(uci_move)
        if success:
            self.board_widget.selected_pos = None
            self.board_widget.update()
            self.update_move_list()
            # If engine is analyzing, we might want to automatically update it
            if self.engine and self.engine.is_analyzing:
                self.start_analysis_request()
                
    def update_move_list(self):
        self.move_list.clear()
        moves = self.board_logic.move_history
        current_idx = self.board_logic.current_move_index
        
        for i in range(0, len(moves), 2):
            move_num = (i // 2) + 1
            w_move_str = moves[i]['uci']
            b_move_str = moves[i+1]['uci'] if i+1 < len(moves) else ""
            
            item = QListWidgetItem(f"{move_num}. {w_move_str} {b_move_str}")
            
            # Highlighting the row containing the current move
            if i == current_idx or i + 1 == current_idx:
                item.setBackground(QColor("#d1e7dd"))
            elif i > current_idx:
                item.setForeground(QColor("gray"))
                
            self.move_list.addItem(item)
            
        self.move_list.scrollToBottom()
            
    def prev_move(self):
        if self.board_logic.undo_move():
            self.board_widget.selected_pos = None
            self.board_widget.update()
            self.update_move_list()
            if self.engine and self.engine.is_analyzing:
                self.start_analysis_request()

    def next_move(self):
        if self.board_logic.redo_move():
            self.board_widget.selected_pos = None
            self.board_widget.update()
            self.update_move_list()
            if self.engine and self.engine.is_analyzing:
                self.start_analysis_request()

    def new_game(self):
        self.board_logic.start_fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"
        self.board_logic.set_fen(self.board_logic.start_fen, clear_history=True)
        self.board_widget.selected_pos = None
        self.board_widget.update()
        self.update_move_list()
        if self.engine and self.engine.is_analyzing:
            self.start_analysis_request()
            
    def flip_board(self):
        self.board_widget.is_flipped = not getattr(self.board_widget, 'is_flipped', False)
        self.board_widget.update()
        
    def set_fen_dialog(self):
        current_fen = self.board_logic.get_fen()
        text, ok = QInputDialog.getText(self, "Edit Position", "Enter FEN string:", text=current_fen)
        if ok and text:
            try:
                self.board_logic.start_fen = text
                self.board_logic.set_fen(text, clear_history=True)
                self.board_widget.selected_pos = None
                self.board_widget.update()
                self.update_move_list()
                if self.engine and self.engine.is_analyzing:
                    self.start_analysis_request()
            except Exception as e:
                QMessageBox.warning(self, "Invalid FEN", f"Error setting FEN:\n{str(e)}")

    def on_palette_piece_selected(self, char):
        self.board_widget.edit_selected_piece = char

    def clear_board(self):
        self.board_logic.board = [['' for _ in range(9)] for _ in range(10)]
        self.board_widget.update()

    def toggle_edit_mode(self):
        if not self.board_widget.edit_mode:
            # Enter Edit Mode
            self.board_widget.edit_mode = True
            self.board_widget.selected_pos = None
            self.board_widget.update()
            
            self.edit_panel.setVisible(True)
            self.btn_edit_mode.setText("Exit Edit Mode")
            self.btn_edit_mode.setStyleSheet("background-color: #d1e7dd; font-weight: bold;")
            
            # Disable other controls
            self.btn_new_game.setEnabled(False)
            self.btn_load_pgn.setEnabled(False)
            self.btn_set_fen.setEnabled(False)
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            
            self.turn_combo.setCurrentIndex(0 if self.board_logic.turn == 'w' else 1)
            
            # Stop engine
            if self.engine and self.engine.is_analyzing:
                self.stop_analysis()
                self.btn_start_analysis.setEnabled(False)
        else:
            # Exit Edit Mode
            self.board_widget.edit_mode = False
            self.edit_panel.setVisible(False)
            self.btn_edit_mode.setText("Enter Edit Mode")
            self.btn_edit_mode.setStyleSheet("")
            
            # Enable controls
            self.btn_new_game.setEnabled(True)
            self.btn_load_pgn.setEnabled(True)
            self.btn_set_fen.setEnabled(True)
            self.btn_prev.setEnabled(True)
            self.btn_next.setEnabled(True)
            if self.engine:
                self.btn_start_analysis.setEnabled(True)
            
            # Apply changes
            self.board_logic.turn = 'w' if self.turn_combo.currentIndex() == 0 else 'b'
            new_fen = self.board_logic.get_fen()
            
            try:
                self.board_logic.start_fen = new_fen
                self.board_logic.set_fen(new_fen, clear_history=True)
            except Exception as e:
                pass # Already set basically
                
            self.board_widget.update()
            self.update_move_list()
            if self.engine:
                self.start_analysis_request()

    def load_pgn(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open PGN", "", "PGN Files (*.pgn);;All Files (*)")
        if file_name:
            with open(file_name, 'r') as f:
                self.board_logic.load_pgn(f.read())
            self.board_widget.update()
            self.update_move_list()

    def save_pgn(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save PGN", "", "PGN Files (*.pgn);;All Files (*)")
        if file_name:
            with open(file_name, 'w') as f:
                f.write(self.board_logic.save_pgn())

    def load_engine(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Engine Executable", "", "Executables (*.exe);;All Files (*)")
        if file_name:
            if self.engine:
                self.engine.quit_engine()
            self.engine = EngineClient(file_name)
            self.engine.analysis_updated.connect(self.on_analysis_update)
            self.engine.bestmove_found.connect(self.on_bestmove)
            if self.engine.start_engine():
                self.btn_start_analysis.setEnabled(True)
                self.engine_log.append(f"Engine loaded: {file_name}")

    def start_analysis_request(self):
        if self.engine:
            if self.engine.is_analyzing:
                self.pending_analysis_restart = True
                self.engine.stop()
            else:
                self.start_analysis()

    def start_analysis(self):
        if self.engine:
            self.engine_log.clear()
            fen = self.board_logic.start_fen
            moves = self.board_logic.get_moves_list()
            self.engine.set_position(fen, moves)
            self.engine.go_infinite()
            self.btn_stop_analysis.setEnabled(True)
            self.btn_start_analysis.setEnabled(False)
            self.pending_analysis_restart = False

    def stop_analysis(self):
        if self.engine:
            self.pending_analysis_restart = False
            self.engine.stop()
            self.btn_stop_analysis.setEnabled(False)
            self.btn_start_analysis.setEnabled(True)

    def on_analysis_update(self, info_str):
        self.engine_log.append(info_str)
        scrollbar = self.engine_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Parse score and PV
        parts = info_str.split(" ")
        try:
            if "score" in parts and "pv" in parts:
                score_idx = parts.index("score")
                pv_idx = parts.index("pv")
                
                score_type = parts[score_idx+1]
                score_val = int(parts[score_idx+2])
                
                # Convert score
                if score_type == "cp":
                    # Pikafish score is from engine's perspective (usually side to move)
                    # Standard GUI convention: + is good for Red, - is good for Black.
                    display_score = score_val / 100.0
                    if self.board_logic.turn == 'b': display_score = -display_score
                    self.engine_score_label.setText(f"Score: {display_score:+.2f}")
                elif score_type == "mate":
                    self.engine_score_label.setText(f"Score: Mate in {abs(score_val)}")
                
                # Parse PV
                pv_moves = parts[pv_idx+1:pv_idx+6] # Take top 5 moves from PV
                
                # We need to translate PV moves into Chinese notation using a temporary board state
                temp_board = Board(self.board_logic.get_fen())
                
                # If the first move is not legal, this info line is likely from a previous analysis state. Ignore it.
                if pv_moves and not temp_board.is_legal_move(pv_moves[0]):
                    return
                    
                chinese_pv = []
                for move in pv_moves:
                    chinese_pv.append(temp_board.uci_to_chinese(move))
                    temp_board.make_move_uci(move, validate=False)
                    
                self.engine_pv_label.setText("Recommended Line: " + " ".join(chinese_pv))
        except Exception as e:
            print("Error parsing info:", e)

    def on_bestmove(self, bestmove):
        self.engine_log.append(f"<b>Best move: {bestmove}</b>")
        self.engine.is_analyzing = False
        self.btn_start_analysis.setEnabled(True)
        self.btn_stop_analysis.setEnabled(False)
        
        # If we had a pending restart request (e.g. from a user move), start the new analysis now
        if getattr(self, 'pending_analysis_restart', False):
            self.start_analysis()

    def closeEvent(self, event):
        if self.engine:
            self.engine.quit_engine()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
