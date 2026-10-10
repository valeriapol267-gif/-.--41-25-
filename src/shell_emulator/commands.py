"""Команды эмулятора: ls, cd, who, tail, cat, rmdir, mv и служебные."""

import getpass
from datetime import datetime

from shell_emulator.vfs import (
    VfsError,
    is_dir,
    is_file,
    join_path,
    list_dir,
    move_node,
    parent_path,
    remove_node,
    resolve_path,
    save_vfs,
)

DEFAULT_TAIL_LINES = 10
LOGIN_TIME = datetime.now().strftime("%Y-%m-%d %H:%M")

current_vfs = None
current_dir = "/"


class CommandError(Exception):
    """Ошибка выполнения команды: команда не найдена или не удалась."""


class ExitCommand(Exception):
    """Сигнал о том, что пользователь хочет выйти из программы."""


def set_vfs(vfs):
    """Запомнить загруженную VFS и встать в её корневую папку."""
    global current_vfs, current_dir
    current_vfs = vfs
    current_dir = "/"


def need_vfs():
    """Вернуть загруженную VFS или сообщить, что её нет."""
    if current_vfs is None:
        raise CommandError("VFS не загружена")
    return current_vfs


def cmd_ls(args):
    """Команда ls [путь]: показать содержимое папки VFS."""
    vfs = need_vfs()
    if len(args) > 1:
        raise CommandError("ls: слишком много аргументов")

    target = current_dir
    if len(args) == 1:
        target = resolve_path(current_dir, args[0])

    if is_dir(vfs, target):
        return "\n".join(list_dir(vfs, target))
    if is_file(vfs, target):
        return target.split("/")[-1]
    raise CommandError("ls: нет такого файла или каталога: " + args[0])


def cmd_cd(args):
    """Команда cd [путь]: сменить текущую папку внутри VFS."""
    global current_dir
    vfs = need_vfs()
    if len(args) > 1:
        raise CommandError("cd: слишком много аргументов")

    if len(args) == 0:
        current_dir = "/"
        return ""

    target = resolve_path(current_dir, args[0])
    if is_file(vfs, target):
        raise CommandError("cd: не каталог: " + args[0])
    if not is_dir(vfs, target):
        raise CommandError("cd: нет такого каталога: " + args[0])

    current_dir = target
    return ""


def cmd_who(args):
    """Команда who: кто работает в системе (имя, терминал, время входа)."""
    if len(args) > 0:
        raise CommandError("who: команда не принимает аргументов")
    return getpass.getuser() + "  console  " + LOGIN_TIME


def cmd_cat(args):
    """Команда cat файл...: вывести содержимое файлов VFS."""
    if len(args) == 0:
        raise CommandError("cat: не указан файл")

    parts = []
    for name in args:
        text = read_text(name, "cat")
        parts.append(text.rstrip("\n"))
    return "\n".join(parts)


def cmd_tail(args):
    """Команда tail [-n N] файл: вывести последние N строк файла.

    Без -n выводятся последние DEFAULT_TAIL_LINES строк.
    """
    count = DEFAULT_TAIL_LINES
    if len(args) >= 1 and args[0] == "-n":
        if len(args) < 2:
            raise CommandError("tail: после -n нужно число строк")
        count = parse_count(args[1])
        args = args[2:]

    if len(args) == 0:
        raise CommandError("tail: не указан файл")
    if len(args) > 1:
        raise CommandError("tail: поддерживается только один файл")

    lines = read_text(args[0], "tail").splitlines()
    start = max(0, len(lines) - count)
    return "\n".join(lines[start:])


def cmd_rmdir(args):
    """Команда rmdir папка...: удалить пустые папки VFS."""
    vfs = need_vfs()
    if len(args) == 0:
        raise CommandError("rmdir: не указана папка")

    for name in args:
        remove_empty_dir(vfs, name)
    return ""


def cmd_mv(args):
    """Команда mv источник назначение: переместить или переименовать."""
    vfs = need_vfs()
    if len(args) != 2:
        raise CommandError("mv: нужно указать источник и назначение")

    src = resolve_path(current_dir, args[0])
    check_move_source(vfs, src, args[0])

    dst = resolve_path(current_dir, args[1])
    target = find_move_target(vfs, src, dst, args[1])

    if is_file(vfs, target):
        remove_node(vfs, target)
    move_node(vfs, src, target)
    return ""


def cmd_exit(args):
    """Команда exit. Останавливает работу эмулятора."""
    raise ExitCommand()


def cmd_vfs_info(args):
    """Команда vfs-info: имя VFS и хеш SHA-256 её данных."""
    vfs = need_vfs()
    return "vfs-info: имя=" + vfs.name + " sha256=" + vfs.info_hash()


def cmd_vfs_save(args):
    """Команда vfs-save путь: сохранить VFS в CSV по указанному пути."""
    vfs = need_vfs()
    if len(args) == 0:
        raise CommandError("vfs-save требует путь для сохранения")

    try:
        save_vfs(vfs, args[0])
    except VfsError as error:
        raise CommandError(str(error))

    return "vfs-save: сохранено в " + args[0]


def parse_count(text):
    """Преобразовать строку в неотрицательное число для tail -n."""
    try:
        count = int(text)
    except ValueError:
        raise CommandError("tail: неверное число строк: " + text)

    if count < 0:
        raise CommandError("tail: неверное число строк: " + text)
    return count


def remove_empty_dir(vfs, arg):
    """Удалить одну пустую папку или сообщить, почему нельзя."""
    path = resolve_path(current_dir, arg)

    if path == "/":
        raise CommandError("rmdir: нельзя удалить корневой каталог")
    if is_file(vfs, path):
        raise CommandError("rmdir: " + arg + ": не каталог")
    if not is_dir(vfs, path):
        raise CommandError("rmdir: " + arg + ": нет такого каталога")
    if current_dir == path or current_dir.startswith(path + "/"):
        raise CommandError("rmdir: нельзя удалить текущий каталог")
    if len(list_dir(vfs, path)) > 0:
        raise CommandError("rmdir: " + arg + ": каталог не пуст")

    remove_node(vfs, path)


def check_move_source(vfs, src, arg):
    """Проверить, что источник для mv существует и его можно двигать."""
    if src == "/":
        raise CommandError("mv: нельзя переместить корневой каталог")
    if not is_dir(vfs, src) and not is_file(vfs, src):
        raise CommandError("mv: нет такого файла или каталога: " + arg)
    if current_dir == src or current_dir.startswith(src + "/"):
        raise CommandError("mv: нельзя переместить текущий каталог")


def find_move_target(vfs, src, dst, arg):
    """Вычислить итоговый путь для mv и проверить, что он допустим.

    Если dst - существующая папка, источник кладётся внутрь неё.
    """
    target = dst
    if is_dir(vfs, dst):
        target = join_path(dst, src.split("/")[-1])

    if target == src:
        raise CommandError("mv: источник и назначение совпадают")
    if is_dir(vfs, src) and target.startswith(src + "/"):
        raise CommandError("mv: нельзя переместить каталог в самого себя")
    if not is_dir(vfs, parent_path(target)):
        raise CommandError("mv: нет такого каталога: " + arg)
    if is_dir(vfs, target):
        raise CommandError("mv: не удалось заменить каталог: " + arg)
    if is_file(vfs, target) and is_dir(vfs, src):
        raise CommandError("mv: нельзя заменить файл каталогом: " + arg)
    return target


def read_text(path_arg, command):
    """Прочитать файл VFS как текст.

    command - имя команды для сообщений об ошибках.
    """
    vfs = need_vfs()
    path = resolve_path(current_dir, path_arg)

    if is_dir(vfs, path):
        raise CommandError(command + ": " + path_arg + ": это каталог")
    if not is_file(vfs, path):
        raise CommandError(
            command + ": " + path_arg + ": нет такого файла"
        )

    data = vfs.nodes[path].content_bytes
    return data.decode("utf-8", errors="replace")


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "who": cmd_who,
    "cat": cmd_cat,
    "tail": cmd_tail,
    "rmdir": cmd_rmdir,
    "mv": cmd_mv,
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
    "vfs-save": cmd_vfs_save,
}


def execute(name, args):
    """Найти команду по имени и выполнить её.

    Если команда не найдена в словаре COMMANDS,
    поднимается ошибка CommandError.
    """
    if name not in COMMANDS:
        raise CommandError("неизвестная команда: " + name)

    handler = COMMANDS[name]
    return handler(args)
