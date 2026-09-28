#!/usr/bin/env bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$ROOT/src/main.py"
python3 "$APP" --vfs "$ROOT/vfs" --script "$ROOT/scripts/startup_errors.txt"
python3 "$APP" --script "$ROOT/scripts/missing.txt"
python3 "$APP" --vfs "$ROOT/vfs" --script "$ROOT/scripts/missing.txt"
