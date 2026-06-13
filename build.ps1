# Install dependencies
pip install -r requirements.txt

# Run PyInstaller
# --onedir creates a folder containing the exe and dependencies (better for PyQt apps than --onefile which unpacks everything to Temp first)
# --windowed hides the console
pyinstaller --noconfirm --onedir --windowed --icon=icon.ico --name "YY-Xiangqi" main.py

Write-Host "Build finished. Executable is at dist/YY-Xiangqi/YY-Xiangqi.exe" -ForegroundColor Green
