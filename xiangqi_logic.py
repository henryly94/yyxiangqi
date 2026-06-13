class Board:
    def __init__(self, fen=None):
        self.start_fen = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"
        self.board = [['' for _ in range(9)] for _ in range(10)]
        self.turn = 'w'
        
        self.move_history = []  # List of dicts: {'uci': move, 'piece': piece, 'captured': captured_piece, 'fen': fen_before}
        self.current_move_index = -1
        
        self.fullmove_number = 1
        self.halfmove_clock = 0
        self.set_fen(fen if fen else self.start_fen, clear_history=True)

    def set_fen(self, fen, clear_history=False):
        self.board = [['' for _ in range(9)] for _ in range(10)]
        parts = fen.split(' ')
        rows = parts[0].split('/')
        for r, row_str in enumerate(rows):
            c = 0
            for char in row_str:
                if char.isdigit():
                    c += int(char)
                else:
                    self.board[r][c] = char
                    c += 1
        if len(parts) > 1:
            self.turn = parts[1]
        else:
            self.turn = 'w'
            
        if clear_history:
            self.move_history.clear()
            self.current_move_index = -1

    def get_fen(self):
        fen_rows = []
        for r in range(10):
            row_str = ""
            empty_count = 0
            for c in range(9):
                if self.board[r][c] == '':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += self.board[r][c]
            if empty_count > 0:
                row_str += str(empty_count)
            fen_rows.append(row_str)
        return "/".join(fen_rows) + f" {self.turn} - - {self.halfmove_clock} {self.fullmove_number}"

    def pos_to_uci(self, r, c):
        file_char = chr(ord('a') + c)
        rank_char = str(9 - r)
        return file_char + rank_char

    def uci_to_pos(self, uci_str):
        c = ord(uci_str[0]) - ord('a')
        r = 9 - int(uci_str[1])
        return r, c

    def is_red(self, piece):
        return piece.isupper() if piece else False

    def is_black(self, piece):
        return piece.islower() if piece else False

    def get_piece(self, r, c):
        if 0 <= r < 10 and 0 <= c < 9:
            return self.board[r][c]
        return None

    def _is_pseudo_legal(self, r1, c1, r2, c2, piece):
        if r1 == r2 and c1 == c2: return False
        if not (0 <= r2 < 10 and 0 <= c2 < 9): return False
        
        target = self.board[r2][c2]
        is_red = self.is_red(piece)
        if target and (self.is_red(target) == is_red):
            return False # Cannot capture own piece

        dr = r2 - r1
        dc = c2 - c1
        p = piece.upper()

        if p == 'K': # King
            if is_red:
                if not (7 <= r2 <= 9 and 3 <= c2 <= 5): return False
            else:
                if not (0 <= r2 <= 2 and 3 <= c2 <= 5): return False
            if abs(dr) + abs(dc) != 1: return False
        
        elif p == 'A': # Advisor
            if is_red:
                if not (7 <= r2 <= 9 and 3 <= c2 <= 5): return False
            else:
                if not (0 <= r2 <= 2 and 3 <= c2 <= 5): return False
            if abs(dr) != 1 or abs(dc) != 1: return False

        elif p == 'B': # Elephant
            if is_red:
                if r2 < 5: return False
            else:
                if r2 > 4: return False
            if abs(dr) != 2 or abs(dc) != 2: return False
            # check eye
            eye_r, eye_c = r1 + dr//2, c1 + dc//2
            if self.board[eye_r][eye_c] != '': return False

        elif p == 'N': # Horse
            if abs(dr) == 2 and abs(dc) == 1:
                if self.board[r1 + dr//2][c1] != '': return False
            elif abs(dr) == 1 and abs(dc) == 2:
                if self.board[r1][c1 + dc//2] != '': return False
            else:
                return False

        elif p == 'R': # Chariot
            if dr != 0 and dc != 0: return False
            step_r = (dr // abs(dr)) if dr else 0
            step_c = (dc // abs(dc)) if dc else 0
            cr, cc = r1 + step_r, c1 + step_c
            while (cr, cc) != (r2, c2):
                if self.board[cr][cc] != '': return False
                cr += step_r
                cc += step_c

        elif p == 'C': # Cannon
            if dr != 0 and dc != 0: return False
            step_r = (dr // abs(dr)) if dr else 0
            step_c = (dc // abs(dc)) if dc else 0
            cr, cc = r1 + step_r, c1 + step_c
            mounts = 0
            while (cr, cc) != (r2, c2):
                if self.board[cr][cc] != '': mounts += 1
                cr += step_r
                cc += step_c
            if target == '':
                if mounts != 0: return False
            else:
                if mounts != 1: return False

        elif p == 'P': # Pawn
            if is_red:
                if dr > 0: return False # Cannot go backward
                if dr == 0:
                    if r1 > 4: return False # Cannot go sideways before crossing river
                    if abs(dc) != 1: return False
                elif dr == -1:
                    if dc != 0: return False
                else:
                    return False
            else:
                if dr < 0: return False
                if dr == 0:
                    if r1 < 5: return False
                    if abs(dc) != 1: return False
                elif dr == 1:
                    if dc != 0: return False
                else:
                    return False

        return True

    def _kings_facing(self):
        r_king = b_king = None
        for r in range(10):
            for c in range(9):
                if self.board[r][c] == 'K': r_king = (r, c)
                elif self.board[r][c] == 'k': b_king = (r, c)
        if not r_king or not b_king: return False
        
        if r_king[1] == b_king[1]: # Same file
            for r in range(b_king[0] + 1, r_king[0]):
                if self.board[r][r_king[1]] != '':
                    return False # Blocked
            return True # Kings facing each other
        return False

    def _is_in_check(self, is_red):
        king_char = 'K' if is_red else 'k'
        kr, kc = -1, -1
        for r in range(10):
            for c in range(9):
                if self.board[r][c] == king_char:
                    kr, kc = r, c
                    break
        if kr == -1: return False # Should not happen

        # Check if any opponent piece can pseudo-legal capture the king
        for r in range(10):
            for c in range(9):
                p = self.board[r][c]
                if p and (self.is_red(p) != is_red):
                    if self._is_pseudo_legal(r, c, kr, kc, p):
                        return True
        return False

    def generate_legal_moves(self):
        moves = []
        is_red_turn = (self.turn == 'w')
        for r1 in range(10):
            for c1 in range(9):
                p = self.board[r1][c1]
                if p and (self.is_red(p) == is_red_turn):
                    # Try all possible destinations
                    for r2 in range(10):
                        for c2 in range(9):
                            if self._is_pseudo_legal(r1, c1, r2, c2, p):
                                # Make the move temporarily
                                target = self.board[r2][c2]
                                self.board[r2][c2] = p
                                self.board[r1][c1] = ''
                                
                                legal = not self._is_in_check(is_red_turn) and not self._kings_facing()
                                
                                # Revert
                                self.board[r1][c1] = p
                                self.board[r2][c2] = target
                                
                                if legal:
                                    moves.append(self.pos_to_uci(r1, c1) + self.pos_to_uci(r2, c2))
        return moves

    def is_legal_move(self, uci_move):
        return uci_move in self.generate_legal_moves()

    def undo_move(self):
        if self.current_move_index < 0: return False
        
        last_move = self.move_history[self.current_move_index]
        self.current_move_index -= 1
        
        # Restore state without clearing history
        self.set_fen(last_move['fen'], clear_history=False)
        return True

    def redo_move(self):
        if self.current_move_index >= len(self.move_history) - 1: return False
        self.current_move_index += 1
        next_move = self.move_history[self.current_move_index]
        
        # Manually apply state changes without re-adding to history
        r1, c1 = self.uci_to_pos(next_move['uci'][:2])
        r2, c2 = self.uci_to_pos(next_move['uci'][2:])
        piece = self.board[r1][c1]
        self.board[r2][c2] = piece
        self.board[r1][c1] = ''
        self.turn = 'b' if self.turn == 'w' else 'w'
        if self.turn == 'w':
            self.fullmove_number += 1
            
        return True

    def make_move_uci(self, uci_move, validate=True):
        if validate and not self.is_legal_move(uci_move):
            return False
            
        r1, c1 = self.uci_to_pos(uci_move[:2])
        r2, c2 = self.uci_to_pos(uci_move[2:])
        piece = self.board[r1][c1]
        captured = self.board[r2][c2]
        
        state_record = {
            'uci': uci_move,
            'piece': piece,
            'captured': captured,
            'fen': self.get_fen(),
            'turn': self.turn
        }
        
        self.board[r2][c2] = piece
        self.board[r1][c1] = ''
        self.turn = 'b' if self.turn == 'w' else 'w'
        if self.turn == 'w':
            self.fullmove_number += 1
            
        # If we are making a new move while in history, truncate the future moves
        if self.current_move_index < len(self.move_history) - 1:
            self.move_history = self.move_history[:self.current_move_index + 1]
            
        self.move_history.append(state_record)
        self.current_move_index += 1
        return True

    def get_moves_list(self):
        return [m['uci'] for m in self.move_history[:self.current_move_index + 1]]
        
    def get_all_moves_list(self):
        return [m['uci'] for m in self.move_history]

    def save_pgn(self, event="Casual Game", site="Xiangqi GUI"):
        pgn = f'[Event "{event}"]\n[Site "{site}"]\n[FEN "{self.start_fen}"]\n\n'
        for i in range(0, len(self.move_history), 2):
            move_num = (i // 2) + 1
            w_move = self.move_history[i]['uci']
            b_move = self.move_history[i+1]['uci'] if i+1 < len(self.move_history) else ""
            pgn += f"{move_num}. {w_move} {b_move} "
        return pgn.strip()

    def load_pgn(self, pgn_string):
        self.move_history.clear()
        self.current_move_index = -1
        self.set_fen(self.start_fen) # default
        
        lines = pgn_string.strip().split('\n')
        moves_line = ""
        for line in lines:
            line = line.strip()
            if line.startswith('[FEN "'):
                fen = line.split('"')[1]
                self.set_fen(fen)
                self.start_fen = fen
            elif not line.startswith('[') and line != '':
                moves_line += line + " "
                
        tokens = moves_line.split(' ')
        for token in tokens:
            token = token.strip()
            if not token or '.' in token:
                continue
            if len(token) == 4 and token[0] in 'abcdefghi' and token[1] in '0123456789':
                self.make_move_uci(token, validate=False) # Skip validation for loading performance

    def uci_to_chinese(self, uci_move):
        if len(uci_move) != 4: return uci_move
        r1, c1 = self.uci_to_pos(uci_move[:2])
        r2, c2 = self.uci_to_pos(uci_move[2:])
        piece = self.board[r1][c1]
        if not piece: return uci_move
        
        is_red = self.is_red(piece)
        p = piece.upper()
        
        # Numbers map
        red_nums = ['九', '八', '七', '六', '五', '四', '三', '二', '一']
        black_nums = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        
        c1_name = red_nums[c1] if is_red else black_nums[c1]
        c2_name = red_nums[c2] if is_red else black_nums[c2]
        
        # Piece characters
        piece_chars = {
            'K': '帅', 'A': '仕', 'B': '相', 'N': '马', 'R': '车', 'C': '炮', 'P': '兵',
            'k': '将', 'a': '士', 'b': '象', 'n': '马', 'r': '车', 'c': '炮', 'p': '卒'
        }
        name = piece_chars.get(piece, piece)
        
        # Prefix for same file pieces
        prefix = name
        same_file_pieces = []
        for r in range(10):
            if self.board[r][c1] == piece:
                same_file_pieces.append(r)
        
        if len(same_file_pieces) == 2:
            if is_red:
                front = min(same_file_pieces)
                if r1 == front: prefix = "前" + name
                else: prefix = "后" + name
            else:
                front = max(same_file_pieces)
                if r1 == front: prefix = "前" + name
                else: prefix = "后" + name
            c1_name = "" # Omit start file if prefix used
            
        dr = r2 - r1
        dc = c2 - c1
        
        direction = ""
        if is_red:
            if dr < 0: direction = "进"
            elif dr > 0: direction = "退"
            else: direction = "平"
        else:
            if dr > 0: direction = "进"
            elif dr < 0: direction = "退"
            else: direction = "平"
            
        end_str = ""
        if direction == "平":
            end_str = c2_name
        else:
            if p in ['K', 'R', 'C', 'P']:
                steps = abs(dr)
                if is_red:
                    num_names = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九']
                    end_str = num_names[steps]
                else:
                    end_str = str(steps)
            else:
                end_str = c2_name
                
        return f"{prefix}{c1_name}{direction}{end_str}"

