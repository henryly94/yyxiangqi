# Install dependencies
pip install -r requirements.txt

# Run PyInstaller
# --onedir creates a folder containing the exe and dependencies (better for PyQt apps than --onefile which unpacks everything to Temp first)
# --windowed hides the console
pyinstaller --noconfirm --onedir --windowed --name "XiangqiGUI" main.py

Write-Host "Build finished. Executable is at dist/XiangqiGUI/XiangqiGUI.exe" -ForegroundColor Green
