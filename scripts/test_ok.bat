@echo off
set ROOT=%~dp0..
python "%ROOT%\src\main.py" --vfs "%ROOT%\vfs" --script "%ROOT%\scripts\startup_ok.txt"
python "%ROOT%\src\main.py" --script "%ROOT%\scripts\startup_ok.txt"
python "%ROOT%\src\main.py" --vfs "%ROOT%\vfs"
python "%ROOT%\src\main.py"
