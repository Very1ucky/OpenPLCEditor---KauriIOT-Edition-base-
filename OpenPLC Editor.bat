@echo off
echo "Starting OpenPLC Editor..."
if exist .\new_editor\ (
  rmdir /s /q .\editor
  rmdir /s /q .\matiec\lib
  move .\new_editor .\editor
  move .\new_lib .\matiec\lib
)

if exist ".\python\.venv\" (
  start "" "runas /user:Administrator .\python\.venv\Scripts\python.exe" ".\editor\Beremiz.py"
) else (
  echo "Setting up python virtual environment..."
  ".\python\python.exe" -m venv ".\python\.venv"

  echo "Installing dependencies..."
  copy ".\python\requirements.txt" ".\python\.venv\Scripts\"
  ".\python\.venv\Scripts\python.exe" -m pip install -r requirements.txt

  echo "Starting OpenPLC Editor..."
  start "" "runas /user:admin .\python\.venv\Scripts\pythonw.exe" ".\editor\Beremiz.py"
  
)