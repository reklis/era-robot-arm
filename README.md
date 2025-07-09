# ERA Robot Arm - Flask Web Interface

This project provides a web interface to control an LED connected to GPIO 18 on a Raspberry Pi.

## Features

- Web-based LED control interface
- RESTful API endpoints for LED control
- Static file serving from the `public` folder

## Installation

1. Install dependencies:
```bash
uv sync
```

## Usage

1. Run the Flask application:
```bash
python main.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Use the web interface to control the LED:
   - Click "Turn LED ON" to turn on the LED
   - Click "Turn LED OFF" to turn off the LED

## API Endpoints

- `GET /` - Serves the main web interface
- `POST /led/on` - Turns the LED on
- `POST /led/off` - Turns the LED off
- `GET /led/status` - Gets the LED status (simplified implementation)

## Requirements

- Raspberry Pi with GPIO access
- Python 3.12+
- Flask
- gpiozero
- rpi-lgpio

## Hardware Setup

Connect an LED to GPIO 18 on your Raspberry Pi:
- LED positive (longer leg) → GPIO 18
- LED negative (shorter leg) → Ground (GND)

## Development

The Flask app runs in debug mode by default. For production, set `debug=False` in `main.py`.
