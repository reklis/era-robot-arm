from flask import Flask, send_from_directory, jsonify
from gpiozero import LED
import os
import signal
import atexit
from time import sleep

led = LED(18)
led.on()
sleep(3)
led.off()
sleep(3)
led.close()

