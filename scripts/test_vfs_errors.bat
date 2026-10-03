@echo off
set ROOT=%~dp0..
python "%ROOT%\src\main.py" --vfs "%ROOT%\vfs\invalid.csv"
python "%ROOT%\src\main.py" --vfs "%ROOT%\vfs\missing.csv"
