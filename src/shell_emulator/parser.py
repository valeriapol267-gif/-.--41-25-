"""Парсер, который разбивает строку на команду и аргументы"""


def parse_line(line):
    """Разбить строку ввода на команду и список аргументов"""
    parts = line.split()

    if len(parts) == 0:
        command = ""
        args = []
    else:
        command = parts[0]
        args = parts[1:]

    return command, args
