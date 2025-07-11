from flask import Flask, send_from_directory, jsonify, request
import os
import signal
import atexit
import pigpio
import time

class StepperMotor:
    def __init__(self, pi, dir_pin, step_pin, delay=0.001):
        """
        :param pi: pigpio.pi() instance
        :param dir_pin: GPIO pin for DIR−
        :param step_pin: GPIO pin for PUL−
        :param delay: time between steps (controls speed)
        """
        self.pi = pi
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.delay = delay

        pi.set_mode(self.dir_pin, pigpio.OUTPUT)
        pi.set_mode(self.step_pin, pigpio.OUTPUT)

    def move(self, steps, direction='forward'):
        self.pi.write(self.dir_pin, 1 if direction == 'forward' else 0)
        for _ in range(steps):
            self.pi.write(self.step_pin, 1)
            time.sleep(self.delay)
            self.pi.write(self.step_pin, 0)
            time.sleep(self.delay)

    def cleanup(self):
        self.pi.write(self.dir_pin, 0)
        self.pi.write(self.step_pin, 0)



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

pi = pigpio.pi()
m1 = StepperMotor(pi, dir_pin=17, step_pin=27)

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

