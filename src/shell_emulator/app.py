"""Окно эмулятора: поле вывода и строка ввода команд."""

import tkinter as tk
from tkinter import scrolledtext

from shell_emulator.commands import CommandError, ExitCommand, execute
from shell_emulator.parser import parse_line

VFS_NAME = "vfs"

root = None
output = None
entry = None


def on_enter(event):
    line = entry.get()
    entry.delete(0, tk.END)
    print_line("> " + line)
    handle_line(line)


def handle_line(line):
    command, args = parse_line(line)

    if command == "":
        return

    try:
        result = execute(command, args)
        print_line(result)
    except ExitCommand:
        root.quit()
    except CommandError as error:
        print_line("Ошибка: " + str(error))


def print_line(text):
    output.configure(state="normal")
    output.insert(tk.END, text + "\n")
    output.configure(state="disabled")
    output.see(tk.END)


def main():
    
    global root, output, entry

    root = tk.Tk()
    root.title("Эмулятор - [" + VFS_NAME + "]")

    output = scrolledtext.ScrolledText(
        root, state="disabled", width=80, height=24
    )
    output.pack(fill="both", expand=True)

    entry = tk.Entry(root)
    entry.pack(fill="x")
    entry.bind("<Return>", on_enter)
    entry.focus_set()

    root.mainloop()
