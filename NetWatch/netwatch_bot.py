#!/usr/bin/env python3

from datetime import datetime as dt

cfg = {}

###############################################################################
def led_send_cmd(cmd):
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((cfg["lumen1_addr"], cfg["lumen1_port"]))
            sock.sendall(cmd.encode())
    except:
        pass
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('localhost', cfg["lport"]))
            sock.sendall(cmd.encode())
    except:
        pass

###############################################################################
def netscan(nm):
    _ = nm.scan(hosts="10.11.4.0/24", arguments="-sn")
    return dt.now().day, set(nm.all_hosts())

###############################################################################
def get_mac_linux(ip):
    import subprocess, re
    output = subprocess.check_output(["arp", "-n", ip], text=True)
    pattern = re.compile(r"([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})")
    m = pattern.search(output)
    return m.group(1) if m else None

###############################################################################
def main():
    import time, nmap
    nm = nmap.PortScanner()
    then = None
    lit = False
    brained = False
    while True:
        # Scan the network
        if then != dt.now().day:
            # Refresh baseline at midnight
            then, baseline = netscan(nm)
            past, current = baseline, baseline
            lit, brained = True, False
        else:
            # Routine scan
            past = current
            _, current = netscan(nm)

        print(lit, brained, baseline, current - baseline, flush=True)

        # Play custom animation if conditions are met
        if baseline < current:
            for ip in current - baseline:
                if not brained and get_mac_linux(ip) == "ac:3e:b1:03:34:d1":
                    # Play Braaains animation
                    led_send_cmd("braaains_anim")
                    lit, brained = True, True
                else:
                    # Play other animations
                    pass

        # Turn the lights on/off as appropriate
        if lit and baseline >= current and baseline >= past:
            # Everyone disconnected, turn off
            led_send_cmd("lightsaber_off")
            lit = False
        elif lit or baseline < past and baseline < current:
            # Someone new steadily connected, turn on
            led_send_cmd("lightsaber_on")
            lit = True

        time.sleep(60)

###############################################################################
if __name__ == '__main__':
    import os
    assert "LED_SERVICE_PORT" in os.environ
    assert "LUMEN1_ADDR"      in os.environ
    assert "LUMEN1_PORT"      in os.environ
    cfg["lport"] = int(os.environ["LED_SERVICE_PORT"])
    cfg["lumen1_addr"] = os.environ["LUMEN1_ADDR"]
    cfg["lumen1_port"] = int(os.environ["LUMEN1_PORT"])

    main()

