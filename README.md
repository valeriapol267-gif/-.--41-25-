# Эмулятор языка оболочки ОС

Учебный проект по дисциплине «Конфигурационное управление»
(ИКБО-41-25, Вариант №22). Практическая работа №1, этапы 1-3.

## 1. Общее описание

Эмулятор командной строки UNIX-подобной ОС с графическим
интерфейсом (GUI). Поддерживает настройку через параметры
командной строки, выполнение стартового скрипта и загрузку
виртуальной файловой системы (VFS) из CSV-файла.

## 2. Описание всех функций и настроек

- Окно с заголовком `Эмулятор - [vfs]`, полем вывода и строкой ввода.
- Парсер разбивает ввод на команду и аргументы по пробелам.
- Команды-заглушки: `ls`, `cd` (выводят имя и аргументы), `exit`.
- Параметры командной строки:
  - `--vfs ПУТЬ` - путь к CSV-файлу VFS;
  - `--script ПУТЬ` - путь к стартовому скрипту.
- При запуске в окно выводятся параметры и информация о VFS ([debug]).
- Стартовый скрипт выполняется построчно, ошибочные строки
  пропускаются с номером строки, ввод и вывод видны в окне.
- VFS хранится только в памяти, источник - CSV-файл со столбцами
  `path,type,content`. `type` - `dir` или `file`, содержимое файлов
  закодировано в base64. Вложенность задаётся самим путём
  (например `/docs/projects/2024/report.txt`).
- `vfs-info` - вывести имя загруженной VFS и SHA-256 её исходных
  данных.
- `vfs-save путь` - сохранить текущее состояние VFS в CSV по
  указанному пути, в исходном формате.
- Ошибка загрузки VFS (файл не найден или неверный формат CSV)
  выводится в окно, приложение продолжает работать без VFS.

## 3. Описание команд для сборки проекта и запуска тестов

Зависимости не нужны (только стандартная библиотека Python).

    python3 src/main.py [--vfs ПУТЬ] [--script ПУТЬ]

Скрипты для проверки разных вариантов VFS:

    scripts\test_vfs_minimal.bat   (Windows, минимальная VFS)
    scripts\test_vfs_small.bat     (Windows, несколько файлов)
    scripts\test_vfs_nested.bat    (Windows, 3+ уровня вложенности)
    scripts\test_vfs_errors.bat    (Windows, ошибки загрузки VFS)
    bash scripts/test_vfs_minimal.sh   (Linux/macOS)
    bash scripts/test_vfs_small.sh
    bash scripts/test_vfs_nested.sh
    bash scripts/test_vfs_errors.sh

## 4. Примеры использования

    python3 src/main.py --vfs vfs/nested.csv --script scripts/startup_full.txt

В окне появится:

    [debug] Параметры запуска:
    [debug] vfs = vfs/nested.csv
    [debug] script = scripts/startup_full.txt
    [debug] VFS загружена: имя=nested.csv
    [debug] VFS sha256=5e355743c9f7c8fa7257f5266eb2cdfcc78bd471c1ef36b1cfd45b88f2baa6ea
    $ ls
    ls
    $ cd projects
    cd projects
    $ vfs-info
    vfs-info: имя=nested.csv sha256=5e355743c9f7c8fa7257f5266eb2cdfcc78bd471c1ef36b1cfd45b88f2baa6ea
    $ vfs-save vfs/saved_output.csv
    vfs-save: сохранено в vfs/saved_output.csv
    $ foo bar
    Ошибка (строка 5 скрипта): неизвестная команда: foo

Ошибка загрузки VFS (`scripts/test_vfs_errors.bat`):

    [debug] vfs = vfs/invalid.csv
    Ошибка загрузки VFS: неверный формат CSV: нужны столбцы path,type,content
