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
MV_ARGS_COUNT = 2
KILO = 1024
DIR_SIZE = 4096
LS_LETTERS = "lha"
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


def resolve(vfs, arg, command):
    """Полный путь для аргумента команды или CommandError."""
    try:
        return resolve_path(vfs, current_dir, arg)
    except VfsError as error:
        raise CommandError(command + ": " + str(error))


def parse_ls_args(args):
    """Разделить аргументы ls на буквы опций и пути."""
    letters = ""
    paths = []
    for arg in args:
        if arg.startswith("-") and len(arg) > 1:
            for letter in arg[1:]:
                if letter not in LS_LETTERS:
                    raise CommandError("ls: неизвестная опция: -" + letter)
                letters += letter
        else:
            paths.append(arg)
    return letters, paths


def entry_size(vfs, path):
    """Размер узла в байтах (для папки условно 4096)."""
    if is_dir(vfs, path):
        return DIR_SIZE
    return len(vfs.nodes[path].content_bytes)


def format_size(size, human):
    """Записать размер числом или в виде 4.0K, 1.5M (для опции -h)."""
    if not human:
        return str(size)
    value = float(size)
    for unit in ["", "K", "M", "G"]:
        if value < KILO or unit == "G":
            if unit == "":
                return str(size)
            return "%.1f%s" % (value, unit)
        value = value / KILO


def make_entries(vfs, target, show_all):
    """Собрать список (имя, путь) для вывода ls."""
    if is_file(vfs, target):
        return [(target.split("/")[-1], target)]

    entries = []
    if show_all:
        entries.append((".", target))
        entries.append(("..", parent_path(target)))
    for name in list_dir(vfs, target):
        if show_all or not name.startswith("."):
            entries.append((name, join_path(target, name)))
    return entries


def format_entries(vfs, entries, letters):
    """Собрать текст ответа ls: короткий список или подробный (-l)."""
    if len(entries) == 0:
        return ""
    if "l" not in letters:
        return "\n".join(name for name, path in entries)

    sizes = []
    for name, path in entries:
        sizes.append(format_size(entry_size(vfs, path), "h" in letters))
    width = max(len(text) for text in sizes)

    lines = []
    for i in range(len(entries)):
        name, path = entries[i]
        kind = "d" if is_dir(vfs, path) else "-"
        lines.append(kind + " " + sizes[i].rjust(width) + " " + name)
    return "\n".join(lines)


def cmd_ls(args):
    """Команда ls [-l] [-h] [-a] [путь]: содержимое папки VFS.

    -a показывает скрытые файлы, . и ..; -l выводит тип и размер;
    -h делает размеры читаемыми. Опции можно писать слитно (-lah).
    """
    vfs = need_vfs()
    letters, paths = parse_ls_args(args)
    if len(paths) > 1:
        raise CommandError("ls: слишком много аргументов")

    target = current_dir
    if len(paths) == 1:
        target = resolve(vfs, paths[0], "ls")
    if not is_dir(vfs, target) and not is_file(vfs, target):
        raise CommandError("ls: нет такого файла или каталога: " + paths[0])

    entries = make_entries(vfs, target, "a" in letters)
    return format_entries(vfs, entries, letters)


def cmd_cd(args):
    """Команда cd [путь]: сменить текущую папку внутри VFS."""
    global current_dir
    vfs = need_vfs()
    if len(args) > 1:
        raise CommandError("cd: слишком много аргументов")

    if len(args) == 0:
        current_dir = "/"
        return ""

    target = resolve(vfs, args[0], "cd")
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
        if len(args) == 1:
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
    if len(args) != MV_ARGS_COUNT:
        raise CommandError("mv: нужно указать источник и назначение")

    src = resolve(vfs, args[0], "mv")
    check_move_source(vfs, src, args[0])

    dst = resolve(vfs, args[1], "mv")
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
    path = resolve(vfs, arg, "rmdir")

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
    path = resolve(vfs, path_arg, command)

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