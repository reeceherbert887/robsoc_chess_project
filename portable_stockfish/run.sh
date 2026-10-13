#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
if [[ ! -x .venv/bin/python || ! -x engine/stockfish ]]; then
    echo 'First run ./setup.sh from this folder.' >&2
    exit 1
fi
exec .venv/bin/python app.py
