from flask import Flask, send_from_directory, jsonify, request
import os
import signal
import atexit
import time
import threading
from gpiozero import DigitalOutputDevice, Servo

class StepperMotor:
    def __init__(self, dir_pin, pul_pin, delay=0.001):
        self.dir = DigitalOutputDevice(dir_pin)
        self.pul = DigitalOutputDevice(pul_pin)
        self.delay = delay
        self.running = threading.Event()
        self.direction = 'forward'
        self.thread = None

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

    def continuous_step(self):
        while True:
            if self.running.is_set():
                if self.direction == 'forward':
                    self.dir.on()
                else:
                    self.dir.off()
                
                self.pul.on()
                time.sleep(self.delay)
                self.pul.off()
                time.sleep(self.delay)
            else:
                time.sleep(0.01)

    def start_continuous(self, direction='forward'):
        self.direction = direction
        self.running.set()

    def stop_continuous(self):
        self.running.clear()

    def cleanup(self):
        self.running.clear()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        self.dir.close()
        self.pul.close()

app = Flask(__name__)


# GPIO cleanup functions
def cleanup_gpio():
    """Clean up GPIO resources"""
    try:
        for motor in motors:
            motor.cleanup()
        wrist.close()
        claw.close()
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

m1 = StepperMotor(dir_pin=5, pul_pin=6)
m2 = StepperMotor(dir_pin=16, pul_pin=20)
m3 = StepperMotor(dir_pin=17, pul_pin=27)
m4 = StepperMotor(dir_pin=22, pul_pin=23)
m5 = StepperMotor(dir_pin=24, pul_pin=25)

motors = [m1, m2, m3, m4, m5]

for motor in motors:
    motor.thread = threading.Thread(target=motor.continuous_step, daemon=True)
    motor.thread.start()

wrist = Servo(13)
claw = Servo(12)

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('public', filename)

@app.route('/wrist', methods=['POST'])
def set_wrist():
    try:
        value = float(request.json.get('value'))
        value = max(-1.0, min(1.0, value))  # Clamp
        wrist.value = value
        return jsonify({'success': True, 'value': value})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/claw', methods=['POST'])
def set_claw():
    try:
        value = float(request.json.get('value'))
        value = max(-1.0, min(1.0, value))  # Clamp
        claw.value = value
        return jsonify({'success': True, 'value': value})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/m1', methods=['POST'])
def control_m1():
    try:
        enabled = bool(request.json.get('enabled'))
        direction = request.json.get('direction', 'forward')
        if enabled:
            m1.start_continuous(direction)
        else:
            m1.stop_continuous()
        return jsonify({'success': True, 'enabled': enabled})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/m2', methods=['POST'])
def control_m2():
    try:
        enabled = bool(request.json.get('enabled'))
        direction = request.json.get('direction', 'forward')
        if enabled:
            m2.start_continuous(direction)
        else:
            m2.stop_continuous()
        return jsonify({'success': True, 'enabled': enabled})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/m3', methods=['POST'])
def control_m3():
    try:
        enabled = bool(request.json.get('enabled'))
        direction = request.json.get('direction', 'forward')
        if enabled:
            m3.start_continuous(direction)
        else:
            m3.stop_continuous()
        return jsonify({'success': True, 'enabled': enabled})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/m4', methods=['POST'])
def control_m4():
    try:
        enabled = bool(request.json.get('enabled'))
        direction = request.json.get('direction', 'forward')
        if enabled:
            m4.start_continuous(direction)
        else:
            m4.stop_continuous()
        return jsonify({'success': True, 'enabled': enabled})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/m5', methods=['POST'])
def control_m5():
    try:
        enabled = bool(request.json.get('enabled'))
        direction = request.json.get('direction', 'forward')
        if enabled:
            m5.start_continuous(direction)
        else:
            m5.stop_continuous()
        return jsonify({'success': True, 'enabled': enabled})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

