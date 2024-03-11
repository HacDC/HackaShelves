#!/bin/bash
# This script must be run as root.
# Edit hacka_shelves.env before installing.

CONFIG_DIR=/etc
INSTALL_DIR=/usr/local/bin
SYSTEMD_DIR=/etc/systemd/system

# Install depencies
apt-get install -y nmap
python3 -m pip install -r requirements.txt

# Install the fan-control script for the X715 power management hat
cp FanControl/pwm_fan_control.py ${INSTALL_DIR}
chmod 0700 ${INSTALL_DIR}/pwm_fan_control.py

# Install the configuration script for the Discord bot and the LED controller service
if [ ! -f ${CONFIG_DIR}/hacka_shelves.env ]
then
	echo "Installing config file"
	cp hacka_shelves.env ${CONFIG_DIR}
	chmod 0640 ${CONFIG_DIR}/hacka_shelves.env
	chown root:daemon ${CONFIG_DIR}/hacka_shelves.env
else
	echo "Preserving existing config file"
fi

# Function that enables and starts a systemd service
install_service() {
    local srv_name=$1
    systemctl stop ${srv_name}
    cp systemd/${srv_name}.service ${SYSTEMD_DIR}
    systemctl daemon-reload
    systemctl enable ${srv_name}
    systemctl start  ${srv_name}
}

# Install the LED server (merge all python scripts into one)
cat LEDServer/hacdc_strip.py LEDServer/hacdc_server.py > ${INSTALL_DIR}/led_server.py
chmod 0700 ${INSTALL_DIR}/led_server.py
install_service led

if [ "$HOSTNAME" == "lumen0" ]
then
    # Install the sound server
    cp SndServer/snd_server.py ${INSTALL_DIR}
    chmod 0700 ${INSTALL_DIR}/snd_server.py
    chown hacdc:hacdc ${INSTALL_DIR}/snd_server.py
    install_service snd

    # Install the Discord bot
    cp DiscordBot/discord_bot.py ${INSTALL_DIR}
    chmod 0700 ${INSTALL_DIR}/discord_bot.py
    chown nobody:daemon ${INSTALL_DIR}/discord_bot.py
    install_service discord

    # Install the NetWatch bot
    cp NetWatch/netwatch_bot.py ${INSTALL_DIR}
    chmod 0700 ${INSTALL_DIR}/netwatch_bot.py
    chown nobody:daemon ${INSTALL_DIR}/netwatch_bot.py
    install_service netwatch
fi

# Restart systemd for good measure
systemctl daemon-reload

