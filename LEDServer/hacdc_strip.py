#!/usr/bin/env python3

from rpi_ws281x import Color, PixelStrip, ws, RGBW
from typing import List
import numpy as np
import time

###############################################################################
class HacDCStrip:
    # Simple class that can control several LED strips at once
    def __init__(self,
            pins:     List[int],
            lengths:  List[int],
            sections: List[int],
            brightness: int,
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
        self.dbg = debug

        self.states = np.zeros((self.cnt, self.max), dtype=int)

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
        pass

    def flicker_off(self):
        pass

    ###########################################################################
    def let_me_in_anim(self, sec: int = 0, repeat: int = 5, wait_ms: int = 500):
        if not 0 <= sec < self.nsc:
            print(f"let_me_in_anim: invalid section: {sec}")
            return
        start, end = self.sec[sec], self.sec[sec+1]
        for r0 in range(repeat):
            for r1 in range(2):
                for strip in range(self.cnt):
                    if start < self.len[strip]:
                        self.blinkStrip(strip, start, end, Color(192,0,0,0))
            time.sleep(wait_ms/1000.)

    ###########################################################################
    def blinkStrip(
            self, strip: int, start: int, end: int,
            col: RGBW, wait_ms: int = 100):
        states = self.states.copy()
        for p in range(start, end):
            self.setPixelColor(strip, p, col)
        self.show()
        #self.strips[strip].show()
        time.sleep(wait_ms/1000.)
        for p in range(start, end):
            self.setPixelColor(strip, p, int(states[strip, p]))
        self.show()
        #self.strips[strip].show()

    ###########################################################################
    # These functions write on all strips at once
    def setXStripColor(self, start: int, end: int, col: RGBW):
        for p in range(start, end):
            self.setXPixelColor(p, col)

    def setXPixelColor(self, n: int, col: RGBW):
        for strip in range(self.states.shape[0]):
            self.setPixelColor(strip, n, col)

    ###########################################################################
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

