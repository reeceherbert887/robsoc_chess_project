#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$SCRIPT_DIR"

echo "========================================"
echo "    RobSoc Chess — Installation"
echo "========================================"

echo ""
echo "[1/4] Checking system dependencies..."

sudo apt update
sudo apt install -y python3 python3-venv python3-tk fonts-dejavu-core

echo ""
echo "[2/4] Setting up Python environment..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

.venv/bin/python -m pip install -r requirements.txt

echo ""
echo "[3/4] Checking official Stockfish engine..."

mkdir -p engine

if [ -f engine/stockfish ] && [ ! -d engine/stockfish ]; then

    echo "Existing Stockfish executable found."

else

    # Handle an extracted archive directory named stockfish.
    if [ -d engine/stockfish ]; then
        mv engine/stockfish "engine/stockfish-extracted-$(date +%Y%m%d-%H%M%S)"
    fi

    if [ -f engine/stockfish-official ]; then

        echo "Using existing official Stockfish executable..."
        cp engine/stockfish-official engine/stockfish

    elif [ -f "$REPO_DIR/stockfish-linux-x86-64-universal.tar.gz" ]; then

        echo "Extracting official Stockfish archive..."

        temp_dir="$(mktemp -d)"
        trap 'rm -rf "$temp_dir"' EXIT

        tar -xzf "$REPO_DIR/stockfish-linux-x86-64-universal.tar.gz" \
            -C "$temp_dir"

        cp "$temp_dir/stockfish/stockfish-linux-x86-64-universal" \
            engine/stockfish

    else

        echo "ERROR: Official Stockfish archive not found."
        echo "Place stockfish-linux-x86-64-universal.tar.gz"
        echo "in the repository root."
        exit 1

    fi
fi

chmod +x engine/stockfish

echo ""
echo "[4/4] Testing Stockfish..."

if printf "uci\nquit\n" | ./engine/stockfish | grep -q "uciok"; then
    echo "Stockfish UCI test successful!"
else
    echo "ERROR: Stockfish UCI test failed."
    exit 1
fi

echo ""
echo "========================================"
echo " Installation completed successfully!"
echo "========================================"
echo ""
echo "Launch Robo Chess using:"
echo "  ./run.sh"
