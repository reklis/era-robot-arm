from flask import Flask, send_from_directory, jsonify, request
import os
import signal
import atexit
import time
from gpiozero import DigitalOutputDevice
from gpiozero.pins.lgpio import LGPIOFactory

class StepperMotor:
    def __init__(self, dir_pin, pul_pin, delay=0.001):
        # Use LGPIOFactory for non-root access on Pi 5
        self.factory = LGPIOFactory()
        self.dir = DigitalOutputDevice(dir_pin, pin_factory=self.factory)
        self.pul = DigitalOutputDevice(pul_pin, pin_factory=self.factory)
        self.delay = delay

    def step(self, steps, direction='forward'):
        self.dir.value = 1 if direction == 'forward' else 0
        for _ in range(steps):
            self.pul.on()
            time.sleep(self.delay)
            self.pul.off()
            time.sleep(self.delay)

    def cleanup(self):
        self.dir.close()
        self.pul.close()

app = Flask(__name__)


# GPIO cleanup functions
def cleanup_gpio():
    """Clean up GPIO resources"""
    try:
        m1.cleanup()
        print("GPIO resources cleaned up successfully")
    except Exception as e:
        print(f"Error during GPIO cleanup: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"Received signal {signum}, cleaning up...")
    cleanup_gpio()
    exit(0)

# Register cleanup handlers
atexit.register(cleanup_gpio)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

m1 = StepperMotor(dir_pin=17, pul_pin=27)

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('public', filename)

@app.route('/claw', methods=['POST'])
def set_claw():
    try:
        value = float(request.json.get('value'))
        value = max(-1.0, min(1.0, value))  # Clamp
        claw.value = value
        return jsonify({'success': True, 'value': value})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/m1/move', methods=['POST'])
def move_m1():
    try:
        m1.move(request.json.get('steps'), request.json.get('direction'))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

