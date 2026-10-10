"""Окно эмулятора: поле вывода и строка ввода команд."""

import tkinter as tk
from tkinter import scrolledtext

from shell_emulator.commands import CommandError, ExitCommand, execute, \
    set_vfs
from shell_emulator.parser import parse_line
from shell_emulator.vfs import VfsError, load_vfs

VFS_NAME = "vfs"
SCRIPT_DELAY_MS = 100

root = None
output = None
entry = None


def on_enter(event):
    """Вызывается при нажатии Enter в строке ввода."""
    line = entry.get()
    entry.delete(0, tk.END)
    print_line("$ " + line)
    handle_line(line)


def handle_line(line, where=""):
    """Разобрать и выполнить строку. Вернуть True, если был exit."""
    command, args = parse_line(line)

    if command == "":
        return False

    try:
        result = execute(command, args)
        if result != "":
            print_line(result)
            
    except ExitCommand:
        root.quit()
        return True
    except CommandError as error:
        print_line("Ошибка" + where + ": " + str(error))

    return False


def print_line(text):
    """Напечатать строку текста в поле вывода."""
    output.configure(state="normal")
    output.insert(tk.END, text + "\n")
    output.configure(state="disabled")
    output.see(tk.END)


def show_params(args):
    """Вывести в окно отладочную информацию о параметрах запуска."""
    vfs = args.vfs or "(не задан)"
    script = args.script or "(не задан)"
    print_line("[debug] Параметры запуска:")
    print_line("[debug] vfs = " + vfs)
    print_line("[debug] script = " + script)


def load_vfs_from_args(args):
    """Загрузить VFS, если путь указан в параметрах запуска."""
    if args.vfs == "":
        return

    try:
        loaded = load_vfs(args.vfs)
    except VfsError as error:
        print_line("Ошибка загрузки VFS: " + str(error))
        return

    set_vfs(loaded)
    print_line("[debug] VFS загружена: имя=" + loaded.name)
    print_line("[debug] VFS sha256=" + loaded.info_hash())


def run_script(path):
    """Выполнить стартовый скрипт: показать ввод и вывод строк."""
    try:
        with open(path, encoding="utf-8") as file:
            lines = file.read().splitlines()
    except (OSError, ValueError) as error:
        print_line("Ошибка скрипта: " + str(error))
        return

    for number, line in enumerate(lines, start=1):
        print_line("$ " + line)
        where = " (строка " + str(number) + " скрипта)"
        if handle_line(line, where):
            break


def main(args):
    """Создать окно, загрузить VFS и запустить программу."""
    global root, output, entry

    root = tk.Tk()
    root.title("Эмулятор - [" + VFS_NAME + "]")

    entry = tk.Entry(root)
    entry.pack(side="bottom", fill="x")
    entry.bind("<Return>", on_enter)

    output = scrolledtext.ScrolledText(
        root, state="disabled", width=80, height=24
    )
    output.pack(fill="both", expand=True)
    entry.focus_set()

    show_params(args)
    load_vfs_from_args(args)

    if args.script != "":
        root.after(SCRIPT_DELAY_MS, run_script, args.script)

    root.mainloop()
