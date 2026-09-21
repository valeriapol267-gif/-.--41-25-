"""Тесты модуля shell_emulator.parser."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shell_emulator.parser import parse_line  # noqa: E402


def test_parse_simple_command():
    """Команда без аргументов разбирается корректно."""
    command, args = parse_line("ls")
    assert command == "ls"
    assert args == []


def test_parse_command_with_args():
    """Команда с несколькими аргументами разбирается корректно."""
    command, args = parse_line("cd folder1 folder2")
    assert command == "cd"
    assert args == ["folder1", "folder2"]


def test_parse_empty_line():
    """Пустая строка возвращает пустую команду без аргументов."""
    command, args = parse_line("   ")
    assert command == ""
    assert args == []
