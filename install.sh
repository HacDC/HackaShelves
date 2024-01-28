#!/bin/bash
# This script must be run as root.
# Edit hacka_shelves.env before installing.

CONFIG_DIR=/etc
INSTALL_DIR=/usr/local/bin
SYSTEMD_DIR=/etc/systemd/system

# Install python depencies
python3 -m pip install RPi.GPIO discord 

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

# Install the LED server (merge all python scripts into one)
cat LEDServer/hacdc_strip.py LEDServer/hacdc.server.py > ${INSTALL_DIR}/led_server.py
chmod 0700 ${INSTALL_DIR}/led_server.py

# Install the Discord bot
cp DiscordBot/discord_bot.py ${INSTALL_DIR}
chmod 0700 ${INSTALL_DIR}/discord_bot.py
chown nobody:daemon ${INSTALL_DIR}/discord_bot.py

# Install the systemd service scripts
cp systemd/*.service ${SYSTEMD_DIR}
for srv in systemd/*.service
do
	srv_name=$(basename ${srv})
	systemctl enable ${srv_name}
	systemctl start  ${srv_name}
done

# Restart systemd for good measure
systemctl daemon-reload

