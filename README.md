# F1 Telemetry Simulator

A Python-based simulation of a Formula 1 telemetry system designed to explore how vehicle data is transmitted, processed, and monitored by a race engineer in real time.

This project was built while learning socket programming in class and applies TCP/IP networking concepts to a motorsport-style telemetry environment.

---

## Overview

The system simulates a Formula 1 pit wall receiving telemetry from multiple cars.  
Each car sends telemetry packets containing performance data such as speed, RPM, and G-force.

The server processes incoming data, updates the virtual garage state, and triggers alerts for race engineers when critical thresholds are exceeded.

---

## System Architecture

Car Client → Telemetry Server → Alert Detection → Race Engineer Output

Multiple vehicles can send telemetry simultaneously, simulating the data flow of a two-car Formula 1 team garage.

---

## Features

- Real-time telemetry streaming using TCP socket programming
- Multi-car simulation environment
- Race engineer alert system for safety and performance thresholds
- Simulated race context including track, session, and weather
- Logging of telemetry events

---

## Example Telemetry Signals

- Speed (SPD)
- Engine RPM
- G-force impact detection
- Fuel level
- Tyre wear

Example packet:

CAR23 SPD 315

---

## Example Alerts

- Overspeed warnings
- Heavy braking detection
- 9G+ impact detection
- Tyre degradation alerts

These simulate the types of notifications a race engineer might monitor during a session.

---

## Files

telemetry_server.py  
Main telemetry server that receives and processes vehicle data.

telemetry_client.py  
Simulated car client sending telemetry packets.

williams_race_data.log  
Example telemetry log generated during a simulated session.

---

## What I Learned

- TCP/IP socket programming and client-server architecture
- How real-time telemetry systems must handle multiple data streams
- How safety and performance thresholds can trigger automated alerts
- How motorsport teams rely on telemetry to monitor vehicle performance

---

## Possible Future Improvements

- Implement UDP-based telemetry to simulate lower-latency communication
- Add a graphical telemetry dashboard
- Introduce additional telemetry signals such as throttle position and brake pressure
- Add data visualization for race engineers
