# HackaShelves

## Content

- `DiscordBot       `: Bot that monitors channel #let-me-in on Discord and blinks the lights red when someone posts
- `NetWatch         `: Bot that monitors the local network and turns on the lights when someone connects
- `FanControl       `: Basic fan controller for the Raspberry Pi
- `LEDServer        `: Service that listens for commands on port 5000 and controls the LEDs
- `SndServer        `: Service that listens for commands on port 4000 and plays sounds
- `hacka_shelves.env`: Configuration file (do not git commit your Discord token!)
- `install.sh       `: Installation script to run with sudo
- `systemd          `: Scripts used to automatically start all services on reboot

## Install

1. Edit hacka\_shelves.env and set you Discord bot token
2. Run: `sudo ./install.sh`
3. Check if the services run properly:
    -  `journalctl -fn100 -u discord`
    -  `journalctl -fn100 -u netwatch`
    -  `journalctl -fn100 -u snd`
    -  `journalctl -fn100 -u led`
    -  `journalctl -fn100 -u fan`

## Dev

To add new animations, edit `LEDServer/hacdc_strip.py`. New animation method
names should end with `_on`, `_off` or `_anim`.

## LED Control

For now, the port is only open locally, so you have to SSH into the Pi:
```
$ ssh hacdc@lumen0
$ echo CMD | nc localhost 5000
$ echo let_me_in_anim | nc localhost 5000
$ echo let_me_in_anim 1 3 1000 | nc localhost 5000
```
CMD can be:
- `lightsaber\_on` / `lightsaber_off`
- `instant\_on` / `instant_off`
- `flicker_on` / `flickr_off`
- `let\_me\_in\_anim`

Parameters depend on the method called, RTFC.

## Sound Control

Add your mp3 of choice to `/home/hacdc/mp3`. To play it:
```
$ ssh hacdc@lumen0
$ echo filename.mp3 | nc localhost 4000
```
The Pi must be connected to a bluetooth speaker, for now:
```
$ bluetoothctl connect 40:ef:4c:1d:70:a1
```

## Dev

You can start the LED server manually in debug mode to have a nice GUI:
```
cd LEDServer
sudo LED_DEBUG=1 LED_SERVICE_PORT=5000 python3 hacdc.server.py
```

