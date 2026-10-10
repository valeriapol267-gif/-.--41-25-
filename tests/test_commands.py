"""Тесты модуля shell_emulator.commands."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shell_emulator import commands  # noqa: E402
from shell_emulator.commands import (  # noqa: E402
    CommandError,
    ExitCommand,
    execute,
    set_vfs,
)
from shell_emulator.vfs import Vfs, VfsNode  # noqa: E402


def make_vfs():
    """Собрать небольшую VFS прямо в памяти для тестов."""
    log_text = "\n".join("строка " + str(i) for i in range(1, 13))
    nodes = {
        "/": VfsNode("/", True),
        "/a.txt": VfsNode("/a.txt", False, "один\nдва\n".encode("utf-8")),
        "/docs": VfsNode("/docs", True),
        "/docs/b.txt": VfsNode("/docs/b.txt", False, b"bbb"),
        "/log.txt": VfsNode("/log.txt", False, log_text.encode("utf-8")),
    }
    return Vfs("test.csv", nodes, b"raw")


@pytest.fixture(autouse=True)
def loaded_vfs():
    """Перед каждым тестом загружать свежую VFS."""
    set_vfs(make_vfs())


def test_ls_root():
    """ls без аргументов показывает корень."""
    assert execute("ls", []) == "a.txt\ndocs\nlog.txt"


def test_ls_path_and_file():
    """ls умеет показывать папку по пути и отдельный файл."""
    assert execute("ls", ["docs"]) == "b.txt"
    assert execute("ls", ["a.txt"]) == "a.txt"


def test_cd_changes_directory():
    """После cd относительные пути считаются от новой папки."""
    execute("cd", ["docs"])
    assert execute("ls", []) == "b.txt"
    execute("cd", [".."])
    assert commands.current_dir == "/"


def test_cd_errors():
    """cd сообщает об ошибках: нет папки, это файл, много аргументов."""
    for args in (["nope"], ["a.txt"], ["docs", "x"]):
        with pytest.raises(CommandError):
            execute("cd", args)


def test_cat_one_and_many_files():
    """cat выводит один файл или несколько подряд."""
    assert execute("cat", ["docs/b.txt"]) == "bbb"
    assert execute("cat", ["a.txt", "docs/b.txt"]) == "один\nдва\nbbb"


def test_cat_errors():
    """cat сообщает об ошибках: нет файла, папка, нет аргументов."""
    for args in (["nope"], ["docs"], []):
        with pytest.raises(CommandError):
            execute("cat", args)


def test_tail_default_and_n():
    """tail выводит 10 строк по умолчанию и N строк с ключом -n."""
    assert len(execute("tail", ["log.txt"]).splitlines()) == 10
    assert execute("tail", ["-n", "2", "log.txt"]) == "строка 11\nстрока 12"


def test_tail_errors():
    """tail сообщает об ошибках в аргументах и файлах."""
    bad = (["-n"], ["-n", "x", "log.txt"], ["-n", "-1", "log.txt"],
           [], ["nope"], ["docs"], ["a.txt", "log.txt"])
    for args in bad:
        with pytest.raises(CommandError):
            execute("tail", args)


def test_who_prints_user():
    """who выводит имя пользователя и не принимает аргументов."""
    assert "console" in execute("who", [])
    with pytest.raises(CommandError):
        execute("who", ["x"])


def test_commands_need_vfs():
    """Без загруженной VFS ls, cd, cat и tail сообщают об ошибке."""
    set_vfs(None)
    for name in ("ls", "cd", "vfs-info"):
        with pytest.raises(CommandError):
            execute(name, [])
    with pytest.raises(CommandError):
        execute("cat", ["a.txt"])


def test_execute_unknown_command():
    """Неизвестная команда вызывает CommandError."""
    with pytest.raises(CommandError):
        execute("unknown", [])


def test_execute_exit_raises_exit_command():
    """Команда exit вызывает ExitCommand."""
    with pytest.raises(ExitCommand):
        execute("exit", [])
