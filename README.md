# 🚗 AI Smart Parking Occupancy System

Real-time parking space occupancy tracking system using ESP32 Camera, OpenCV, YOLOv8, and Flask.

---

###  Overview
This project processes a live MJPEG stream from a **Deneyap Kart (ESP32)** to analyze parking lot availability. Vehicle detection is powered by **YOLOv8**, and results are displayed on a real-time web dashboard.

###  Tech Stack
* **Hardware:** Deneyap Kart (ESP32 Camera Module)
* **Backend & AI:** Python, OpenCV, Ultralytics YOLOv8
* **Web Interface:** Flask, HTML/CSS, JavaScript

###  Key Features
* Live Wi-Fi video streaming
* Real-time vehicle detection (`car`, `truck`, `bus`, `motorcycle`)
* Interactive ROI editor for parking space configuration (`JSON`)
* Real-time occupancy analytics & web dashboard