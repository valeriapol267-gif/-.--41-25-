"""Команды-заглушки эмулятора: ls, cd и exit."""
class CommandError(Exception):
class ExitCommand(Exception):
def cmd_ls(args):
    return format_call("ls", args)
def cmd_cd(args):
    return format_call("cd", args)
def cmd_exit(args):
    raise ExitCommand()

def format_call(name, args):
    if len(args) == 0:
        return name
    return name + " " + " ".join(args)

COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}


def execute(name, args):
    if name not in COMMANDS:
        raise CommandError("неизвестная команда: " + name)

    handler = COMMANDS[name]
    return handler(args)
