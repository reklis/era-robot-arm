from flask import Flask, send_from_directory, jsonify, request
import os
import signal
import atexit
import time
from gpiozero import DigitalOutputDevice, Servo

class StepperMotor:
    def __init__(self, dir_pin, pul_pin, delay=0.001):
        self.dir = DigitalOutputDevice(dir_pin)
        self.pul = DigitalOutputDevice(pul_pin)
        self.delay = delay

    def step(self, steps, direction='forward'):
        if direction == 'forward':
            self.dir.on()
        else:
            self.dir.off()

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
base = Servo(12)

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('public', filename)

@app.route('/base', methods=['POST'])
def set_base():
    try:
        value = float(request.json.get('value'))
        value = max(-1.0, min(1.0, value))  # Clamp
        base.value = value
        return jsonify({'success': True, 'value': value})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/m1/test', methods=['POST'])
def test_m1():
    try:
        m1.step(200, 'forward')
        m1.step(200, 'backward')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/m1/move', methods=['POST'])
def move_m1():
    try:
        m1.step(request.json.get('steps'), request.json.get('direction'))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

