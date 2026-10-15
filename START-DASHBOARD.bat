@echo off
setlocal
cd /d "%~dp0"
title Anwar Group Finance Dashboard
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" >nul 2>&1
if not errorlevel 1 (
    py -3 server.py
    goto finished
)
python -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" >nul 2>&1
if not errorlevel 1 (
    python server.py
    goto finished
)
echo Python 3.9 or later is required.
echo Install Python 3 from python.org and enable Add Python to PATH.
echo Then double-click START-DASHBOARD.bat again.
:finished
pause
