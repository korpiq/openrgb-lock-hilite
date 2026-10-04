#!/bin/sh
# Installs the daemon as a systemd user service, and enables the
# OpenRGB SDK server it talks to. Needs the `openrgb` and
# `python3-venv` packages (sudo apt install openrgb python3-venv).
set -eu

dir=$(cd "$(dirname "$0")" && pwd)
unit_dir=$HOME/.config/systemd/user

python3 -m venv "$dir/.venv"
"$dir/.venv/bin/pip" install --quiet openrgb-python

mkdir -p "$unit_dir"
sed -e "s|@PYTHON@|$dir/.venv/bin/python|" \
    -e "s|@SCRIPT@|$dir/openrgb_lock_hilite.py|" \
    "$dir/openrgb-lock-hilite.service" > "$unit_dir/openrgb-lock-hilite.service"

systemctl --user daemon-reload
systemctl --user enable --now openrgb.service openrgb-lock-hilite.service
