
# LED strips configuration (top to bottom)
LED_PINS       = (10, 12, 21)
LED_COUNTS     = (60, 60, 36)
LED_SECTIONS   = (36, 60)
LED_BRIGHTNESS = 192

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
def init_led():
    global HacDCStrip
    if "HacDCStrip" not in globals():
        from hacdc_strip import HacDCStrip
    return HacDCStrip(LED_PINS, LED_COUNTS, LED_SECTIONS, LED_BRIGHTNESS, cfg["debug"])

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

    if cfg["debug"]: print(f"\x1b[0G\x1b[2K", end="")
    print(f"CMD {addr[0]}:{addr[1]}: {cmd}", flush=True)

    return cmd

###############################################################################
def run(net, led):
    import re, inspect

    # Command format: keyword int int...
    pattern = re.compile(r"^(\w+)((\s+\d+)*)")

    while True:
        # Recieve a command from a client
        cmd = get_cmd(net)

        # Parse the type of task requested
        if task := pattern.match(cmd):
            meth = task.group(1)
            parm = task.group(2).split() if task.group(2) else []
            parm = [int(p) for p in parm]
        else:
            continue

        # Restrict which methods can be called
        if not meth.endswith(("_on", "_off", "_anim")):
            print(f"Restricted method: {meth}")
            continue

        # Run the method
        if hasattr(led, meth):
            func = getattr(led, meth)
            # Check if this is indeed a method
            if callable(func):
                # Check if the number of parameters checks out
                sig = inspect.signature(func)
                prm = sig.parameters.values()
                req = sum(1 for p in prm if p.default == inspect.Parameter.empty)

                if not req <= len(parm) <= len(prm):
                    print(f"Invalid parameter count for method: {meth}",
                          f"(expected {len(prm)}, got {len(parm)})")
                    continue
                func(*parm)
            else:
                print(f"Invalid method: {meth}")
        else:
            print(f"Unsupported method: {meth}")

###############################################################################
def main():
    try:
        net = init_net()
        led = init_led()
        run(net, led)
    except KeyboardInterrupt:
        pass

    net.close()
    led.lightsaber_off()

###############################################################################
if __name__ == '__main__':
    import os
    assert "LED_SERVICE_PORT" in os.environ
    cfg["lport"] = os.environ["LED_SERVICE_PORT"]
    cfg["lport"] = int(cfg["lport"])
    cfg["debug"] = "LED_DEBUG" in os.environ

    main()
