"""Команды эмулятора: ls, cd, exit, vfs-info, vfs-save."""

from shell_emulator.vfs import VfsError, save_vfs


class CommandError(Exception):
    """Ошибка выполнения команды: команда не найдена или не удалась."""


class ExitCommand(Exception):
    """Сигнал о том, что пользователь хочет выйти из программы."""


current_vfs = None


def set_vfs(vfs):
    """Запомнить загруженную VFS для команд vfs-info и vfs-save."""
    global current_vfs
    current_vfs = vfs


def cmd_ls(args):
    """Команда-заглушка ls. Просто выводит своё имя и аргументы."""
    return format_call("ls", args)


def cmd_cd(args):
    """Команда-заглушка cd. Просто выводит своё имя и аргументы."""
    return format_call("cd", args)


def cmd_exit(args):
    """Команда exit. Останавливает работу эмулятора."""
    raise ExitCommand()


def cmd_vfs_info(args):
    """Команда vfs-info: имя VFS и хеш SHA-256 её данных."""
    if current_vfs is None:
        raise CommandError("VFS не загружена")
    return "vfs-info: имя=" + current_vfs.name + \
        " sha256=" + current_vfs.info_hash()


def cmd_vfs_save(args):
    """Команда vfs-save путь: сохранить VFS в CSV по указанному пути."""
    if current_vfs is None:
        raise CommandError("VFS не загружена")

    if len(args) == 0:
        raise CommandError("vfs-save требует путь для сохранения")

    try:
        save_vfs(current_vfs, args[0])
    except VfsError as error:
        raise CommandError(str(error))

    return "vfs-save: сохранено в " + args[0]


def format_call(name, args):
    """Собрать строку вида 'имя аргумент1 аргумент2'."""
    if len(args) == 0:
        return name
    return name + " " + " ".join(args)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
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
