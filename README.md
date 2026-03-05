# F1 Telemetry Simulator

Python simulation of a Formula 1 telemetry system exploring how vehicle data is transmitted, processed, and monitored by a race engineer in real time.

This project was developed while learning TCP/IP socket programming and applies networking concepts to a motorsport-style telemetry environment.

---

## Overview

The system simulates a Formula 1 pit wall receiving telemetry from multiple race cars.

Each car sends telemetry packets containing vehicle performance data such as speed, RPM, and G-force. The server processes incoming telemetry streams, maintains a virtual garage state, and triggers alerts when safety or performance thresholds are exceeded.

This models the type of real-time telemetry monitoring used by race engineers during a session.

---

## System Architecture

Car Client → Telemetry Server → Alert Detection → Race Engineer Output

Multiple simulated vehicles can transmit telemetry simultaneously, representing a two-car Formula 1 team garage.

---

## Features

- Real-time telemetry streaming using TCP socket programming
- Client-server architecture simulating car-to-pit data transmission
- Multi-car telemetry simulation
- Race engineer alert system for safety and performance thresholds
- Simulated race context including track, session, and weather
- Telemetry event logging

---

## Example Telemetry Signals

- Speed (SPD)
- Engine RPM
- G-force impact detection
- Fuel level
- Tyre wear

Example telemetry packet:

CAR23 SPD 315

---

## Example Alerts

- Overspeed warnings
- Heavy braking detection
- 9G+ impact detection
- Tyre degradation alerts

These simulate the types of notifications a race engineer might monitor during a session.

---

## Project Files

telemetry_server.py  
Main telemetry server that receives and processes incoming telemetry data.

telemetry_client.py  
Simulated vehicle client that sends telemetry packets to the server.

williams_race_data.log  
Example telemetry log generated during a simulated race session.

---

## How to Run

Clone the repository:

git clone https://github.com/eleanorOrad/f1-telemetry-simulator.git

Navigate to the project directory:

cd f1-telemetry-simulator

Start the telemetry server:

python telemetry_server.py

In another terminal window, start a simulated car client:

python telemetry_client.py

Multiple clients can be run simultaneously to simulate multiple race cars sending telemetry data.

---

## What I Learned

- TCP/IP networking and socket programming
- Client-server architecture for real-time systems
- Handling multiple incoming telemetry streams
- Designing automated safety and performance alerts
- Understanding how motorsport teams use telemetry to monitor vehicle performance

---

## Possible Future Improvements

- Implement UDP-based telemetry to simulate lower-latency communication
- Add a graphical telemetry dashboard
- Introduce additional telemetry signals such as throttle position and brake pressure
- Add data visualization tools for race engineers
- Simulate packet loss and latency to test telemetry reliability
