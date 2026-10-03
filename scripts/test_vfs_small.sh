#!/usr/bin/env bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$ROOT/src/main.py"
python3 "$APP" --vfs "$ROOT/vfs/small.csv" --script "$ROOT/scripts/startup_full.txt"
