@echo off
REM Starts the Flask API (port 5000) and the Next.js website (port 3000).
cd /d "%~dp0"
python -m pip install -q -r requirements.txt
if not exist web\node_modules (pushd web & call npm install & popd)
start "KV2 Alumni API" cmd /k python app.py
start "KV2 Alumni Web" cmd /k "cd web && npm run dev"
echo Open http://localhost:3000 in your browser.
