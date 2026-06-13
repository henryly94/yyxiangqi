# YY Xiangqi

A modern, feature-rich graphical user interface for Xiangqi (Chinese Chess), built in Python using PyQt6.

This application is designed for professional analysis, game review, and custom board setups. It fully supports standard UCI (Universal Chess Interface) engines like [Pikafish](https://github.com/official-pikafish/Pikafish) for evaluating positions and generating precise "Best Move" recommendations in standard Chinese Algebraic Notation (e.g., `炮二平五`).

## Features

- **UCI Engine Integration**: Load any standard Xiangqi engine executable. Features real-time, perfectly synced background analysis with centipawn/mate score evaluations and Recommended Line translations.
- **Strict Move Validation**: Enforces all Xiangqi rules, including piece-specific movement restrictions, capturing logic, checks, and the "Flying General" rule.
- **Interactive Visual Board Editor**: Enter "Edit Mode" to access a piece palette. Quickly design custom puzzles, endgames, or specific board states by clicking pieces onto the board.
- **Advanced Move History**: Navigate through move history without deleting future timelines. Branch into new timelines by making alternative moves while exploring the past.
- **Board Flipping**: Instantly invert the board rendering to view from Black's perspective.
- **PGN & FEN Support**: Save your games to standard PGN files, load historic matches, or paste raw FEN strings to instantly set up complex positions.

## Installation and Usage

### Prerequisites
- Python 3.10+
- `pip`

### Run Locally
Clone the repository and install the required dependencies:
```bash
git clone https://github.com/your-username/yy-xiangqi.git
cd yy-xiangqi
pip install -r requirements.txt
```

Launch the GUI:
```bash
python main.py
```

### Loading an Engine
1. Download a compatible engine like [Pikafish](https://github.com/official-pikafish/Pikafish/releases).
2. Click **Load Engine** in the GUI and select the downloaded `.exe` file.
3. Click **Start Analysis** to begin evaluating the current board.

## Building the Executable (Windows)

This repository includes scripts to bundle the Python application into a standalone `.exe` using PyInstaller.

### Local Build
Run the provided PowerShell script:
```powershell
.\build.ps1
```
The compiled standalone directory will be located at `dist/YY-Xiangqi/`.

### Automated GitHub Actions Build
The project includes a GitHub Actions workflow (`.github/workflows/build.yml`). Whenever you push changes to the `main` branch or publish a new Release, GitHub will automatically build the Windows executable and attach it as a downloadable `.zip` artifact under the Actions tab.
