"""Команды-заглушки эмулятора: ls, cd и exit."""


class CommandError(Exception):
    """Ошибка выполнения команды: команда не найдена."""


class ExitCommand(Exception):
    """Сигнал о том, что пользователь хочет выйти из программы."""


def cmd_ls(args):
    """Команда-заглушка ls. Просто выводит своё имя и аргументы."""
    return format_call("ls", args)


def cmd_cd(args):
    """Команда-заглушка cd. Просто выводит своё имя и аргументы."""
    return format_call("cd", args)


def cmd_exit(args):
    """Команда exit. Останавливает работу эмулятора."""
    raise ExitCommand()


def format_call(name, args):
    """Собрать строку вида 'имя аргумент1 аргумент2'."""
    if len(args) == 0:
        return name
    return name + " " + " ".join(args)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
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
