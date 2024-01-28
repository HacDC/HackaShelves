#!/usr/bin/env python3

import discord

cfg = {}

###############################################################################
def led_send_cmd(cmd):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', cfg["lport"]))
        sock.sendall(cmd.encode())


###############################################################################
def main():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = discord.Client(intents=intents)

    ###########################################################################
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        # Filter messages from #let-me-in
        if message.channel.name == "let-me-in":
            print(message.channel.name, message.content)
            assert message.channel.id == 1136099267556163655
            led_send_cmd("let_me_in_anim")
    ###########################################################################

    bot.run(cfg["token"])

###############################################################################
if __name__ == '__main__':
    import os
    assert "DISCORD_TOKEN"    in os.environ
    assert "LED_SERVICE_PORT" in os.environ
    cfg["token"] = os.environ["DISCORD_TOKEN"]
    cfg["lport"] = os.environ["LED_SERVICE_PORT"]
    cfg["lport"] = int(cfg["lport"])

    main()

