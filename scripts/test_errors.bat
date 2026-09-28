@echo off
set ROOT=%~dp0..
python "%ROOT%\src\main.py" --vfs "%ROOT%\vfs" --script "%ROOT%\scripts\startup_errors.txt"
python "%ROOT%\src\main.py" --script "%ROOT%\scripts\missing.txt"
python "%ROOT%\src\main.py" --vfs "%ROOT%\vfs" --script "%ROOT%\scripts\missing.txt"
