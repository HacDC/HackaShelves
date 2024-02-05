#!/usr/bin/env python3

from rpi_ws281x import Color, PixelStrip, ws, RGBW
from typing import List
import numpy as np
import random
import time
import math

###############################################################################
class HacDCStrip:
    # Simple class that can control several LED strips at once
    def __init__(self,
            pins:     List[int],
            lengths:  List[int],
            sections: List[int],
            brightness: int,
            snd_port: int,
            debug: bool = False):

        assert 0 < brightness < 256
        assert len(pins) == len(lengths)
        assert max(lengths) == sections[-1]

        self.pin = pins
        self.len = lengths
        self.sec = (0, *sections)
        self.bri = brightness
        self.cnt = len(pins)
        self.max = max(lengths)
        self.nsc = len(sections)
        self.spt = snd_port
        self.dbg = debug

        # Build a list of all LED sections
        self.sections = []
        for strip in range(self.cnt):
            for sec in range(self.nsc):
                if self.len[strip] >= self.sec[sec+1]:
                    self.sections += [(strip, self.sec[sec], self.sec[sec+1])]
        self.states = np.zeros((self.cnt, self.max), dtype=int)

        # Initialize the LED strips
        self.strips = [PixelStrip(
                lengths[s], pins[s],
                brightness=brightness,
                strip_type=ws.SK6812_STRIP_RGBW
            ) for s in range(self.cnt)]
        for strip in self.strips:
            strip.begin()

    ###########################################################################
    # Instant on/off
    def instant_on(self):
        self.setXStripColor(0, self.max, Color(0,0,0,self.bri))
        self.show()

    def instant_off(self):
        self.setXStripColor(0, self.max, Color(0,0,0,0))
        self.show()

    def section_on(self, sec: int):
        if 0 <= sec < self.nsc:
            self.setXStripColor(self.sec[sec], self.sec[sec+1], Color(0,0,0,self.bri))
            self.show()

    def section_off(self, sec: int):
        if 0 <= sec < self.nsc:
            self.setXStripColor(self.sec[sec], self.sec[sec+1], Color(0,0,0,0))
            self.show()

    ###########################################################################
    # Rapidly light up the strips from start to end with a short gradient
    def lightsaber_on(self, wait_ms: int = 10, gradient_size: int = 20):
        b1,b2 = 0,0
        for i in range(0, self.max+gradient_size):
            for j in range(max(0, i-gradient_size), min(i, self.max)):
                b = int(self.bri * (i-j) / gradient_size)
                self.setXPixelColor(j, Color(0,0,0,b))
                b2,b1 = b1,b
            self.show(wait_ms)

    def lightsaber_off(self, wait_ms: int = 10, gradient_size: int = 20):
        b1,b2 = 0,0
        for i in range(self.max+gradient_size, 0, -1):
            for j in range(max(0, i-gradient_size), min(i, self.max)):
                b = int(self.bri * (i-j-1) / gradient_size)
                self.setXPixelColor(j, Color(0,0,0,b))
                b2,b1 = b1,b
            self.show(wait_ms)

    ###########################################################################
    def flicker_on(self):
        self.flicker(RGBW(0,0,0,self.bri))

    def flicker_off(self):
        self.flicker(RGBW(0,0,0,0))

    def flicker(self, col: RGBW):
        # Turn on random section with random flickr
        mxr = 2
        for rep0 in range(mxr):
            for sec in random.sample(self.sections, len(self.sections)):
                for rep1 in range(random.randint(1,3)):
                    self.blinkStrip(*sec, col)
                if rep0 == mxr-1 or random.randint(0,1):
                    self.setSectionColor(*sec, col)
                    self.show()

    ###########################################################################
    def let_me_in_anim(self, sec: int = 0, repeat: int = 5, wait_ms: int = 500):
        if not 0 <= sec < self.nsc:
            return
        start, end = self.sec[sec], self.sec[sec+1]
        for r0 in range(repeat):
            for r1 in range(2):
                for strip in range(self.cnt):
                    if start < self.len[strip]:
                        self.blinkStrip(strip, start, end, Color(192,0,0,0))
            time.sleep(wait_ms/1000.)

    ###########################################################################
    def braaains_anim(self):
        states = self.states.copy()
        self.flicker_off()
        time.sleep(2.)
        self.snd_send_cmd("braaains.mp3")
        col = RGBW(111,175,32,0)
        time.sleep(.5)
        for sec in random.sample(self.sections, len(self.sections)):
            self.glowStrip(*sec, col, 1)
        time.sleep(.25)
        self.fadeXStrip(0, self.max, col)
        time.sleep(2.)
        self.flicker_on()

    ###########################################################################
    def blinkStrip(
            self, strip: int, start: int, end: int,
            col: RGBW, wait_ms: int = 100):
        states = self.states.copy()
        self.setSectionColor(strip, start, end, col)
        self.show()
        time.sleep(wait_ms/1000.)
        self.resetSectionColor(strip, start, end, states[strip])
        self.show()

    ###########################################################################
    def glowStrip(
            self, strip: int, start: int, end: int,
            col: RGBW, step: int = 1, wait_ms: int = 20):
        for a in range(0,90,step):
            m = math.sin(math.radians(a))
            c = RGBW(int(col.r*m), int(col.g*m), int(col.b*m), int(col.w*m))
            self.setSectionColor(strip, start, end, c)
            self.show()
            time.sleep(wait_ms/1000.)

    def fadeXStrip(
            self, start: int, end: int,
            col: RGBW, step: int = 1, wait_ms: int = 20):
        for a in range(0,90,step):
            m = math.cos(math.radians(a))
            c = RGBW(int(col.r*m), int(col.g*m), int(col.b*m), int(col.w*m))
            self.setXStripColor(start, end, c)
            self.show()
            time.sleep(wait_ms/1000.)

    ###########################################################################
    # These functions write on all strips at once
    def setXStripColor(self, start: int, end: int, col: RGBW):
        for p in range(start, end):
            self.setXPixelColor(p, col)

    def setXPixelColor(self, n: int, col: RGBW):
        for strip in range(self.states.shape[0]):
            self.setPixelColor(strip, n, col)

    ###########################################################################
    def setSectionColor(self, strip: int, start: int, end: int, col: RGBW):
        for p in range(start, end):
            self.setPixelColor(strip, p, col)

    def resetSectionColor(self, strip: int, start: int, end: int, state: np.ndarray):
        assert state.size >= end >= start, f"{state.size} {end}-{start}={end-start}"
        for p in range(start, end):
            self.setPixelColor(strip, p, int(state[p]))

    def setPixelColor(self, strip: int, n: int, col: RGBW):
        self.states[strip,n] = col
        self.strips[strip].setPixelColor(n, col)

    ###########################################################################
    def show(self, wait_ms: int = 0):
        for strip in self.strips:
            strip.show()
        if self.dbg:
            try:
                print("\x1b[0G" + "\n".join(
                    ["".join([f"\x1b[38;2;{c.r+c.w};{c.g+c.w};{c.b+c.w}m*" for c in [RGBW(p) for p in self.states[s,:self.len[s]]]])
                    for s in range(self.states.shape[0])]), end="")
                print("\x1b[1A" * (self.states.shape[0]-1), end="\033[0m", flush=True)
            except Exception as e:
                print("\033[0m", e, flush=True)
        time.sleep(wait_ms/1000.)

    ###############################################################################
    def snd_send_cmd(self, cmd):
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('localhost', self.spt))
            sock.sendall(cmd.encode())

###############################################################################
