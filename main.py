from flask import Flask, send_from_directory, jsonify
from gpiozero import LED
import os
import signal
import atexit

# Initialize LED on GPIO 18
led = LED(18)

app = Flask(__name__)

# GPIO cleanup functions
def cleanup_gpio():
    """Clean up GPIO resources"""
    try:
        led.close()
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

# Serve static files from the public folder
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('public', filename)

# LED control endpoints
@app.route('/led/<action>', methods=['POST'])
def control_led(action):
    try:
        if action == 'on':
            led.on()
            return jsonify({'success': True, 'message': 'LED turned ON'})
        elif action == 'off':
            led.off()
            return jsonify({'success': True, 'message': 'LED turned OFF'})
        else:
            return jsonify({'success': False, 'error': 'Invalid action. Use "on" or "off"'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Get LED status
@app.route('/led/status', methods=['GET'])
def get_led_status():
    try:
        # Note: gpiozero doesn't have a direct way to check LED state
        # This is a simplified implementation
        return jsonify({'success': True, 'status': 'unknown'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Run the Flask app on port 5000
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

