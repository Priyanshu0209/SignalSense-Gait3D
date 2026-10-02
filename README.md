# SignalSense

Enterprise WiFi Monitoring, RSSI Analytics and Live Visualization Platform.

## Overview
SignalSense is a production-grade WiFi monitoring platform designed to continuously monitor a single authorized WiFi network. It provides real-time visualization of connected devices based on RSSI (Received Signal Strength Indicator), approximating distance (Near, Medium, Far, Very Far, Disconnected).

## Features
- Real-time animated dashboard of connected devices.
- RSSI distance estimation and signal classification.
- Historical data analytics and device statistics.
- Alerts for rapid RSSI drops or connection loss.
- Modular router adapter architecture.

## Getting Started
Copy `.env.example` to `.env` and configure your settings.

### Running with Docker
```bash
docker-compose up -d
```

### Manual Development Setup
See `docs/developer_guide.md` for detailed instructions on running the FastAPI backend and React frontend locally.
