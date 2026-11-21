#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
if command -v xfce4-terminal >/dev/null 2>&1; then
    xfce4-terminal --title="YEN - Secretário Portátil" -e "python3 '$DIR/yen.py'"
elif command -v roxterm >/dev/null 2>&1; then
    roxterm -e "python3 '$DIR/yen.py'"
elif command -v xterm >/dev/null 2>&1; then
    xterm -e "python3 '$DIR/yen.py'"
else
    python3 "$DIR/yen.py"
fi
