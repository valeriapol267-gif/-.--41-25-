@echo off
set ROOT=%~dp0..
python "%ROOT%\src\main.py" --vfs "%ROOT%\vfs\nested.csv" --script "%ROOT%\scripts\startup_full.txt"
