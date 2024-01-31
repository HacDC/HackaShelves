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
def main():
    import time, nmap
    nm = nmap.PortScanner()
    last = None
    lit = False
    while True:
        if last != dt.now().day:
            # Refresh baseline at midnight
            last, baseline = netscan(nm)
            current = baseline
            lit = True
        else:
            _, current = netscan(nm)
        print(lit, baseline, current) # FIXME
        if lit and baseline >= current:
            led_send_cmd("lightsaber_off")
            lit = False
        elif lit or baseline < current:
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

