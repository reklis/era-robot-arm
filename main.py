from flask import Flask, send_from_directory, jsonify
import RPi.GPIO as GPIO
import os
import signal
import atexit


app = Flask(__name__)


import RPi.GPIO as GPIO
import time

class StepperMotor:
    def __init__(self, dir_pin, pul_pin, delay=0.001):
        """
        Initialize the motor control object.
        :param dir_pin: GPIO pin number for DIR−
        :param step_pin: GPIO pin number for PUL−
        :param delay: Delay between steps (in seconds)
        """
        self.dir_pin = dir_pin
        self.step_pin = pul_pin
        self.delay = delay  # Default speed = 1ms = 500 steps/sec

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)

    def move(self, steps, direction='forward'):
        """
        Move the motor a given number of steps.
        :param steps: Number of steps to move
        :param direction: 'forward' or 'backward'
        """
        dir_state = GPIO.HIGH if direction == 'forward' else GPIO.LOW
        GPIO.output(self.dir_pin, dir_state)

        for _ in range(steps):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(self.delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(self.delay)

    def cleanup(self):
        """
        Clean up GPIO state.
        """
        GPIO.cleanup([self.dir_pin, self.step_pin])


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

m1 = StepperMotor(dir_pin=17, pul_pin=27, delay=0.001)

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

