@echo off
REM Start the KV No. 2 Pondicherry alumni portal on http://127.0.0.1:5000
cd /d "%~dp0"
python -m pip install -q -r requirements.txt
python app.py
