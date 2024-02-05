#!/usr/bin/env python3

from datetime import datetime as dt

cfg = {}

###############################################################################
def led_send_cmd(cmd):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', cfg["lport"]))
        sock.sendall(cmd.encode())

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
    while True:
        if then != dt.now().day:
            # Refresh baseline at midnight
            then, baseline = netscan(nm)
            past, current = baseline, baseline
            lit = True
        else:
            past = current
            _, current = netscan(nm)
        print(lit, baseline, past, current) # FIXME
        if lit and baseline >= current and baseline >= past:
            led_send_cmd("lightsaber_off")
            lit = False
        elif not lit and baseline < current:
            for ip in current - baseline:
                print(ip, get_mac_linux(ip), flush=True)
                if get_mac_linux(ip) == "ac:3e:b1:03:34:d1":
                    led_send_cmd("braaains_anim")
                    lit = True
        elif lit or baseline < past and baseline < current:
            led_send_cmd("lightsaber_on")
            lit = True
        time.sleep(60)

###############################################################################
if __name__ == '__main__':
    import os
    assert "LED_SERVICE_PORT" in os.environ
    cfg["lport"] = os.environ["LED_SERVICE_PORT"]
    cfg["lport"] = int(cfg["lport"])

    main()

