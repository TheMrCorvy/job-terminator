#!/usr/bin/env bash
# ==============================================================================
# Job Terminator - Manual Trigger CLI Wrapper (macOS)
# Target Host: Mac Mini 2018 (Intel Core i5) running macOS Sequoia
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/venv/bin/python3"

if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="${ROOT_DIR}/venv/bin/python"
fi

if [ ! -f "$PYTHON_BIN" ]; then
    echo -e "\033[0;31mError: Virtual environment python not found at ${ROOT_DIR}/venv\033[0m"
    echo "Please set up the venv first:"
    echo "  python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"
    exit 1
fi

"$PYTHON_BIN" "${ROOT_DIR}/run_manual.py" "$@"
