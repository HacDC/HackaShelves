
cfg = {}

###############################################################################
def init_net():
    # Create a TCP/IP socket
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    sock.bind(('0.0.0.0', cfg["lport"]))

    # Listen for incoming connections
    sock.listen(1)
    print(f"Waiting for a connections on port {cfg['lport']}...")

    return sock

###############################################################################
def init_led():
    global HacDCStrip
    if "HacDCStrip" not in globals():
        from hacdc_strip import HacDCStrip
    return HacDCStrip(
            cfg["lpins"], cfg["lcnts"], cfg["lsecs"], cfg["lbrit"], cfg["sport"],
            cfg["debug"], (cfg["lumen1_addr"], cfg["lumen1_port"]))

###############################################################################
def get_cmd(net):
    # Wait for a connection
    conn, addr = net.accept()
    conn.settimeout(10.)

    # Receive data in small chunks
    cmd = ""
    try:
        while (c := conn.recv(1).decode()) != "\n":
            cmd += c
    except:
        cmd = cmd.strip()

    if cfg["debug"]: print(f"\x1b[0G\x1b[2K", end="")
    print(f"CMD {addr[0]}:{addr[1]}: {cmd}", flush=True)

    return conn, cmd

def put_res(conn, res):
    try:
        conn.sendall(f"{res}\n".encode())
        conn.close()
    except:
        pass

###############################################################################
def run(net, led):
    import re, inspect

    # Command format: keyword int int...
    pattern = re.compile(r"^(\w+)((\s+\d+)*)")

    while True:
        # Recieve a command from a client
        conn, cmd = get_cmd(net)

        # Parse the type of task requested
        if task := pattern.match(cmd):
            meth = task.group(1)
            parm = task.group(2).split() if task.group(2) else []
            parm = [int(p) for p in parm]
        else:
            put_res(conn, "invalid format")
            continue

        # Restrict which methods can be called
        if not meth.endswith(("_on", "_off", "_anim")):
            print(f"Restricted method: {meth}")
            put_res(conn, "restricted method")
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
                    put_res(conn, "invalid parameters")
                    continue
                func(*parm)
                put_res(conn, "ok")
            else:
                print(f"Invalid method: {meth}")
                put_res(conn, "invalid method")
        else:
            print(f"Unsupported method: {meth}")
            put_res(conn, "unsupported method")

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
    assert "SND_SERVICE_PORT" in os.environ
    assert "LED_PINS"         in os.environ
    assert "LED_COUNTS"       in os.environ
    assert "LED_SECTIONS"     in os.environ
    assert "LED_BRIGHTNESS"   in os.environ
    assert "LUMEN1_ADDR"      in os.environ
    assert "LUMEN1_PORT"      in os.environ

    cfg["lport"] = int(os.environ["LED_SERVICE_PORT"])
    cfg["sport"] = int(os.environ["SND_SERVICE_PORT"])
    cfg["lpins"] = [int(p) for p in os.environ["LED_PINS"].split(",")]
    cfg["lcnts"] = [int(c) for c in os.environ["LED_COUNTS"].split(",")]
    cfg["lsecs"] = [int(s) for s in os.environ["LED_SECTIONS"].split(",")]
    cfg["lbrit"] = int(os.environ["LED_BRIGHTNESS"])
    cfg["lumen1_addr"] = os.environ["LUMEN1_ADDR"]
    cfg["lumen1_port"] = int(os.environ["LUMEN1_PORT"])
    cfg["debug"] = "LED_DEBUG" in os.environ

    main()
