import sys
import time
from engine_client import EngineClient
from xiangqi_logic import Board
from PyQt6.QtCore import QCoreApplication

def main(engine_path):
    app = QCoreApplication(sys.argv)
    engine = EngineClient(engine_path)
    
    def on_info(info):
        print(info)
        
    def on_bestmove(bm):
        print("Got Bestmove:", bm)
        app.quit()
        
    engine.analysis_updated.connect(on_info)
    engine.bestmove_found.connect(on_bestmove)
    
    print(f"Starting engine from {engine_path}...")
    if engine.start_engine():
        print("Engine started successfully.")
        board = Board()
        engine.set_position(board.get_fen())
        engine.go(depth=5) # Shallow depth for quick test
        
        # Start event loop to process signals
        app.exec()
    else:
        print("Failed to start engine.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Please provide the path to pikafish.exe")
