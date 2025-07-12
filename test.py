from gpiozero import DigitalOutputDevice
from gpiozero.pins.lgpio import LGPIOFactory
import time

factory = LGPIOFactory()

dir_pin = DigitalOutputDevice(17, pin_factory=factory)  # DIR−
pul_pin = DigitalOutputDevice(27, pin_factory=factory)  # PUL−

dir_pin.on()

for _ in range(20000):
    pul_pin.off()
    time.sleep(0.001)
    pul_pin.on()
    time.sleep(0.001)

