"""Тесты модуля shell_emulator.commands."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shell_emulator.commands import (
    CommandError,
    ExitCommand,
    execute,
)


def test_execute_ls_with_args():
    """ls возвращает своё имя и переданные аргументы."""
    assert execute("ls", ["-la"]) == "ls -la"


def test_execute_cd_with_args():
    """cd возвращает своё имя и переданные аргументы."""
    assert execute("cd", ["home"]) == "cd home"


def test_execute_unknown_command():
    """Неизвестная команда вызывает CommandError."""
    with pytest.raises(CommandError):
        execute("unknown", [])


def test_execute_exit_raises_exit_command():
    """Команда exit вызывает ExitCommand."""
    with pytest.raises(ExitCommand):
        execute("exit", [])
