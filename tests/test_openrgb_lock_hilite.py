import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from openrgb_lock_hilite import build_colors, parse_hex, read_locks

A, L = (1, 1, 1), (9, 9, 9)
NAMES = ["Key: A", "Key: Caps Lock", "Key: Num Lock", "Key: Scroll Lock"]


def test_parse_hex():
    assert parse_hex("#80355a") == (128, 53, 90)


def test_only_active_locks_are_highlighted():
    locks = {"capslock": True, "numlock": False, "scrolllock": True}
    assert build_colors(NAMES, locks, A, L) == [A, L, A, L]


def test_no_locks_all_ambient():
    locks = {"capslock": False, "numlock": False, "scrolllock": False}
    assert build_colors(NAMES, locks, A, L) == [A] * 4


def test_read_locks_any_device_on(tmp_path):
    for dev, val in [("input3", 0), ("input4", 1)]:
        d = tmp_path / f"{dev}::capslock"
        d.mkdir()
        (d / "brightness").write_text(f"{val}\n")
    state = read_locks(str(tmp_path))
    assert state == {"capslock": True, "numlock": False, "scrolllock": False}
