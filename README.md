# openrgb-lock-hilite

Daemon that colours keyboard keys via [OpenRGB](https://openrgb.org)
by lock state: Caps Lock, Num Lock and Scroll Lock each get their own
colour while active, over an ambient base colour.

Lock state is read from `/sys/class/leds/input*::{capslock,numlock,scrolllock}`;
colours are set through the OpenRGB SDK server.

Target hardware: HyperX Alloy Elite RGB (USB 0951:16be).

## Install

```sh
./install.sh
```

Enables the `openrgb.service` SDK server and this daemon as systemd
user services.

## Configure

Optional `~/.config/openrgb-lock-hilite/config.toml`; keys and defaults
are in `DEFAULT_CONFIG` in `openrgb_lock_hilite.py` (`ambient`, `locked`,
`device`, `[server]`).

## Test

```sh
python3 -m pytest
```
