"""Разбор параметров командной строки эмулятора."""

import argparse


def parse_args(argv=None):
    """Разобрать параметры командной строки.

    --vfs: путь к физическому расположению VFS.
    --script: путь к стартовому скрипту.
    """
    parser = argparse.ArgumentParser(description="Эмулятор оболочки")
    parser.add_argument("--vfs", default="", help="путь к VFS")
    parser.add_argument("--script", default="", help="путь к скрипту")
    return parser.parse_args(argv)
