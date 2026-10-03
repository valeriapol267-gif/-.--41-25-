"""Виртуальная файловая система (VFS), которая живёт в памяти."""

import base64
import binascii
import csv
import hashlib
import io


class VfsError(Exception):
    """Ошибка загрузки или работы с VFS."""


class VfsNode:
    """Один узел VFS: либо папка, либо файл."""

    def __init__(self, path, is_dir, content_bytes=b""):
        self.path = path
        self.is_dir = is_dir
        self.content_bytes = content_bytes


class Vfs:
    """VFS целиком: имя, узлы по путям и исходные байты CSV."""

    def __init__(self, name, nodes, raw_bytes):
        self.name = name
        self.nodes = nodes
        self.raw_bytes = raw_bytes

    def info_hash(self):
        """Вернуть SHA-256 хеш исходных данных VFS в виде строки."""
        return hashlib.sha256(self.raw_bytes).hexdigest()


REQUIRED_COLUMNS = {"path", "type", "content"}


def load_vfs(path):
    """Загрузить VFS из CSV-файла.

    Формат CSV: столбцы path,type,content.
    type - "dir" или "file". Для file содержимое закодировано
    в base64, для dir поле content не используется.
    """
    try:
        with open(path, "rb") as file:
            raw_bytes = file.read()
    except OSError as error:
        raise VfsError("не удалось открыть файл VFS: " + str(error))

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise VfsError("файл VFS не в кодировке UTF-8: " + str(error))

    reader = csv.DictReader(io.StringIO(text))
    fieldnames = reader.fieldnames

    if fieldnames is None or not REQUIRED_COLUMNS.issubset(set(fieldnames)):
        raise VfsError(
            "неверный формат CSV: нужны столбцы path,type,content"
        )

    nodes = {}
    for row in reader:
        node = _row_to_node(row)
        nodes[node.path] = node

    if "/" not in nodes:
        nodes["/"] = VfsNode("/", True)

    name = _name_from_path(path)
    return Vfs(name, nodes, raw_bytes)


def _row_to_node(row):
    """Превратить одну строку CSV в узел VFS."""
    node_path = (row["path"] or "").strip()
    node_type = (row["type"] or "").strip()

    if node_path == "":
        raise VfsError("в CSV встретилась строка с пустым path")

    if node_type == "dir":
        return VfsNode(node_path, True)

    if node_type == "file":
        try:
            content_bytes = base64.b64decode(row["content"] or "")
        except (ValueError, binascii.Error) as error:
            raise VfsError(
                "неверный base64 в файле " + node_path + ": " + str(error)
            )
        return VfsNode(node_path, False, content_bytes)

    raise VfsError("неизвестный тип узла '" + node_type + "' для " + node_path)


def _name_from_path(path):
    """Достать короткое имя файла VFS из полного пути."""
    return path.replace("\\", "/").split("/")[-1]


def save_vfs(vfs, path):
    """Сохранить VFS в CSV-файл в исходном формате."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["path", "type", "content"])

    for node_path in sorted(vfs.nodes):
        node = vfs.nodes[node_path]
        if node.is_dir:
            writer.writerow([node_path, "dir", ""])
        else:
            content = base64.b64encode(node.content_bytes).decode("ascii")
            writer.writerow([node_path, "file", content])

    try:
        with open(path, "w", encoding="utf-8", newline="") as file:
            file.write(output.getvalue())
    except OSError as error:
        raise VfsError("не удалось сохранить VFS: " + str(error))
