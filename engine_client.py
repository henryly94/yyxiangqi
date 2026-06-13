import subprocess
import threading
from PyQt6.QtCore import QObject, pyqtSignal

class EngineClient(QObject):
    # Signals to communicate with the GUI thread
    analysis_updated = pyqtSignal(str) # sends the info string (evaluation, depth, etc.)
    bestmove_found = pyqtSignal(str)

    def __init__(self, engine_path):
        super().__init__()
        self.engine_path = engine_path
        self.process = None
        self.running = False
        self.is_analyzing = False

    def start_engine(self):
        try:
            self.process = subprocess.Popen(
                [self.engine_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1, # Line buffered
                creationflags=subprocess.CREATE_NO_WINDOW # Windows only
            )
            self.running = True
            
            # Start a thread to read engine output
            self.read_thread = threading.Thread(target=self._read_output, daemon=True)
            self.read_thread.start()
            
            # Initialize with UCI
            self.send_command("uci")
            self.send_command("isready")
            return True
        except Exception as e:
            print(f"Failed to start engine: {e}")
            return False

    def send_command(self, cmd):
        if self.process and self.process.stdin and self.running:
            self.process.stdin.write(cmd + "\n")
            self.process.stdin.flush()

    def set_position(self, fen, moves=[]):
        cmd = f"position fen {fen}"
        if moves:
            cmd += " moves " + " ".join(moves)
        self.send_command(cmd)

    def go(self, depth=15):
        self.is_analyzing = True
        self.send_command(f"go depth {depth}")

    def go_infinite(self):
        self.is_analyzing = True
        self.send_command("go infinite")

    def stop(self):
        if self.is_analyzing:
            self.send_command("stop")
            self.is_analyzing = False

    def quit_engine(self):
        if self.running:
            self.send_command("quit")
            self.running = False
            if self.process:
                self.process.terminate()

    def _read_output(self):
        while self.running and self.process and self.process.stdout:
            line = self.process.stdout.readline()
            if not line:
                break
            line = line.strip()
            
            if line.startswith("info"):
                self.analysis_updated.emit(line)
            elif line.startswith("bestmove"):
                parts = line.split(" ")
                if len(parts) > 1:
                    self.bestmove_found.emit(parts[1])
                self.is_analyzing = False
