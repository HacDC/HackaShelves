#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

try:
    fan_pin = 13
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(fan_pin, GPIO.OUT, initial=GPIO.LOW)
    fan = GPIO.PWM(fan_pin, 100)
    fan.start(0)

    while True:
        # Get the CPU's temp
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp = float(f.read()) / 1000.

        match temp:
            case _ if temp > 65.:
                fan.ChangeDutyCycle(100)
            case _ if temp > 60.:
                fan.ChangeDutyCycle(90)
            case _ if temp > 55.:
                fan.ChangeDutyCycle(75)
            case _ if temp > 50.:
                fan.ChangeDutyCycle(50)
            case _ if temp > 30.:
                fan.ChangeDutyCycle(40)
            case _:
                fan.ChangeDutyCycle(0)

        time.sleep(1)

except KeyboardInterrupt:
    fan.ChangeDutyCycle(40)
    GPIO.cleanup()

