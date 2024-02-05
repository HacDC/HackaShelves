#!/usr/bin/env python3

cfg = {}

###############################################################################
def init_net():
    # Create a TCP/IP socket
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    sock.bind(('localhost', cfg["lport"]))

    # Listen for incoming connections
    sock.listen(1)
    print(f"Waiting for a connections on port {cfg['lport']}...")

    return sock

###############################################################################
def get_cmd(net):
    # Wait for a connection
    conn, addr = net.accept()
    conn.settimeout(1.)

    # Receive data in small chunks
    cmd = ""
    try:
        while data := conn.recv(1024):
            cmd += data.decode()
    except:
        cmd = cmd.strip()

    # Close the connection
    conn.close()

    print(f"CMD {addr[0]}:{addr[1]}: {cmd}", flush=True)

    return cmd

###############################################################################
def run(net):
    import os
    os.environ["XDG_RUNTIME_DIR"] = "/run/user/1000"
    os.environ["SDL_AUDIODRIVER"] = "pulse"
    print(os.environ, flush=True)

    import pygame
    pygame.mixer.init()

    while True:
        # Receive a command from a client
        filename = get_cmd(net)

        mp3 = os.path.join(cfg["store"], os.path.basename(filename))
        if os.path.isfile(mp3) and mp3.endswith("mp3"):
            pygame.mixer.music.load(mp3)
            pygame.mixer.music.play()

###############################################################################
def main():
    try:
        net = init_net()
        run(net)
    except KeyboardInterrupt:
        pass

    net.close()

###############################################################################
if __name__ == '__main__':
    import os
    assert "SND_SERVICE_PORT" in os.environ
    assert "SND_SERVICE_DATA" in os.environ
    cfg["store"] = os.environ["SND_SERVICE_DATA"]
    cfg["lport"] = os.environ["SND_SERVICE_PORT"]
    cfg["lport"] = int(cfg["lport"])
    assert os.path.isdir(cfg["store"])

    main()
