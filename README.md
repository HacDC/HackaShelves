# HackaShelves

## Content

- `DiscordBot       `: Bot that monitors channel #let-me-in on Discord and blinks the lights red when someone posts
- `FanControl       `: Basic fan controller for the Raspberry Pi
- `LEDServer        `: Service that listens for commands on port 5000 and controls the LEDs
- `hacka_shelves.env`: Configuration file (do not git commit your Discord token!)
- `install.sh       `: Installation script to run with sudo
- `systemd          `: Scripts used to automatically start all services on reboot

## Install

1. Edit hacka_shelves.env and set you Discord bot token
2. Run: `sudo ./install.sh`
3. Check if the services run properly:
    -  `journalctl -fn100 -u discord`
    -  `journalctl -fn100 -u led`
    -  `journalctl -fn100 -u fan`

## Dev

To add new animations, edit `LEDServer/hacdc_strip.py`. New animation method
names should end with `_on`, `_off` or `_anim`.

