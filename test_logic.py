from xiangqi_logic import Board

def test_logic():
    print("Testing Board initialization...")
    board = Board()
    assert board.turn == 'w'
    
    print("Testing FEN serialization...")
    fen1 = board.get_fen()
    print("Start FEN:", fen1)
    
    print("Testing UCI move make...")
    board.make_move_uci("h2e2") # Right Cannon moves to center
    print("After move history:", board.get_moves_list())
    assert board.turn == 'b'
    
    fen2 = board.get_fen()
    print("FEN after 1 move:", fen2)
    
    print("Testing PGN save...")
    pgn = board.save_pgn()
    print("PGN Output:\n" + pgn)
    
    print("Testing PGN load...")
    board2 = Board()
    board2.load_pgn(pgn)
    print("Loaded move history:", board2.get_moves_list())
    assert board2.get_moves_list() == board.get_moves_list()
    assert board2.get_fen() == board.get_fen()
    
    print("All tests passed.")

if __name__ == '__main__':
    test_logic()
