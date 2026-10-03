@echo off
set ROOT=%~dp0..
python "%ROOT%\src\main.py" --vfs "%ROOT%\vfs\small.csv" --script "%ROOT%\scripts\startup_full.txt"
