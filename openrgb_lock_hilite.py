#!/usr/bin/env python3
"""Colour keyboard keys by lock state through the OpenRGB SDK server."""

import glob
import os
import sys
import time
import tomllib

DEFAULT_CONFIG = {
    "server": {"host": "127.0.0.1", "port": 6742},
    "device": "HyperX Alloy Elite RGB",
    "ambient": "#282c38",
    "locked": "#80355a",
    "poll_seconds": 0.1,
    "refresh_seconds": 5.0,
}

# sysfs LED name suffix -> OpenRGB LED name
LOCK_KEYS = {
    "capslock": "Key: Caps Lock",
    "numlock": "Key: Num Lock",
    "scrolllock": "Key: Scroll Lock",
}

CONFIG_PATH = os.path.expanduser("~/.config/openrgb-lock-hilite/config.toml")


def parse_hex(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def load_config(path=CONFIG_PATH):
    config = {**DEFAULT_CONFIG, "server": dict(DEFAULT_CONFIG["server"])}
    if os.path.exists(path):
        with open(path, "rb") as f:
            user = tomllib.load(f)
        config["server"].update(user.pop("server", {}))
        config.update(user)
    return config


def read_locks(sysfs="/sys/class/leds"):
    """Lock name -> True when any input device reports that LED on."""
    state = {}
    for lock in LOCK_KEYS:
        state[lock] = False
        for path in glob.glob(f"{sysfs}/*::{lock}/brightness"):
            try:
                with open(path) as f:
                    if int(f.read()) > 0:
                        state[lock] = True
            except (OSError, ValueError):
                pass
    return state


def build_colors(led_names, locks, ambient, locked):
    """One colour per LED: ambient, except the keys of active locks."""
    active = {LOCK_KEYS[lock].lower() for lock, on in locks.items() if on}
    return [
        locked if name.lower() in active else ambient for name in led_names
    ]


class Keyboard:
    def __init__(self, config):
        from openrgb import OpenRGBClient
        from openrgb.utils import RGBColor

        self._rgb = RGBColor
        server = config["server"]
        self.client = OpenRGBClient(
            address=server["host"], port=server["port"], name="lock-hilite"
        )
        matches = [d for d in self.client.devices if d.name == config["device"]]
        if not matches:
            names = [d.name for d in self.client.devices]
            raise RuntimeError(f"device {config['device']!r} not in {names}")
        self.device = matches[0]
        self.device.set_mode("direct")
        self.led_names = [led.name for led in self.device.leds]
        missing = [k for k in LOCK_KEYS.values() if k not in self.led_names]
        if missing:
            print(f"warning: LEDs not found: {missing}", file=sys.stderr)

    def apply(self, colors):
        self.device.set_colors([self._rgb(*c) for c in colors])


def run(config):
    ambient = parse_hex(config["ambient"])
    locked = parse_hex(config["locked"])
    keyboard = None
    last_state = None
    last_applied = 0.0
    while True:
        try:
            if keyboard is None:
                keyboard = Keyboard(config)
                last_state = None
            state = read_locks()
            now = time.monotonic()
            if state != last_state or now - last_applied > config["refresh_seconds"]:
                keyboard.apply(
                    build_colors(keyboard.led_names, state, ambient, locked)
                )
                last_state, last_applied = state, now
            time.sleep(config["poll_seconds"])
        except Exception as e:
            print(f"error: {e}; retrying", file=sys.stderr)
            keyboard = None
            time.sleep(5)


if __name__ == "__main__":
    run(load_config())
