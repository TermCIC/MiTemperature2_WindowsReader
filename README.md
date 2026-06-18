<div align="center">

<img src="https://raw.githubusercontent.com/TermCIC/MiTemperature2_WindowsReader/main/new_logo.png" width="128" alt="ReadMi Logo" />

# ReadMi

**Windows BLE Data Logger for Xiaomi LYWSD03MMC Sensors**

![Version](https://img.shields.io/badge/version-v3.0.0-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-orange)

Turn your cheap Xiaomi LYWSD03MMC sensors (~$5 each) into a full environmental datalogger — scan, name, fetch, and export historical temperature & humidity records as CSV, all from a clean desktop GUI.

</div>

---

## Screenshots

<p align="center">
  <img src="https://github.com/TermCIC/MiTemperature2_WindowsReader/assets/32321661/008159ab-862c-459a-854d-f261d8ef7dd1" width="270" />
  <img src="https://github.com/TermCIC/MiTemperature2_WindowsReader/assets/32321661/42409374-1218-45f3-8ff4-001a33c0e85d" width="270" />
  <img src="https://github.com/TermCIC/MiTemperature2_WindowsReader/assets/32321661/76909a2c-c337-4bcd-9b52-010fbf21e7bf" width="270" />
</p>

---

## Features

- **BLE Scan** — Discover all nearby LYWSD03MMC sensors within 30 seconds
- **Live Readings** — Instantly view current temperature, humidity, and battery level
- **Historical Data Export** — Download full min/max records with timestamps as CSV
- **Custom Sensor Names** — Label each sensor for easy identification
- **Real-time Activity Log** — Track every scan, connection attempt, and fetch status
- **Persistent Storage** — Sensor list and names saved across sessions
- **Single-file EXE** — Compile to a standalone Windows executable (no Python needed)

---

## Why Xiaomi LYWSD03MMC?

| Feature | Value |
|---|---|
| Price | ~$5 USD |
| Protocol | Bluetooth Low Energy (BLE) |
| Measurement | Temperature + Humidity |
| History storage | Up to ~150 min/max records |
| Battery life | 1+ year on 2× AA batteries |

The sensor stores interval min/max records internally — ReadMi connects and pulls the full history, making it ideal for long-term environmental monitoring without a constantly-running PC.

---

## Installation

### Option A — Run from source

```bash
# 1. Clone the repository
git clone https://github.com/TermCIC/MiTemperature2_WindowsReader.git
cd MiTemperature2_WindowsReader

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
python main.py
```

### Option B — Build a standalone EXE

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --add-data "web;web" --icon=readmi.ico --name ReadMi main.py
# Output: dist\ReadMi.exe
```

---

## How to Use

1. **Launch** `ReadMi.exe` (or `python main.py`)
2. Click **Scan for sensors** — waits 30 seconds for BLE discovery
3. Sensors appear in the left panel with their status (`Available` / `Unavailable`)
4. Optionally give each sensor a custom name and click **Save**
5. Click **Fetch data** on an available sensor to download its history
6. The CSV file is saved in the same folder as the app:
   ```
   DATA_name_<SensorName>_t_<timestamp>.csv
   ```
7. Monitor progress in the **Activity Log** on the right

### CSV Output Format

| Column | Description |
|---|---|
| Index | Record index from sensor memory |
| Timestamp | Date and time of the recorded interval |
| Min Temp | Minimum temperature (°C) |
| Max Temp | Maximum temperature (°C) |
| Min Humidity | Minimum relative humidity (%) |
| Max Humidity | Maximum relative humidity (%) |

---

## Tech Stack

| Component | Library / Tool |
|---|---|
| BLE communication | [Bleak](https://github.com/hbldh/bleak) 0.22.3 |
| Desktop GUI bridge | [Eel](https://github.com/python-eel/Eel) 0.18.1 |
| Async I/O | Python `asyncio` |
| Frontend | HTML + CSS + Vanilla JS |
| Packaging | PyInstaller |

---

## Sensor Hardware Tip

The LYWSD03MMC runs on a CR2032 coin cell by default. For long-term deployment, you can wire two AA batteries to the sensor's battery contacts. This extends runtime to **over a year**, making it a cost-effective wireless datalogger for field research.

---

## Changelog

### v3.0.0 — 2026-06-18
- Complete UI redesign: modern card layout, status badges, reading chips
- Sensor cards now update live (Available/Unavailable status refreshes in real-time)
- Latest sensor readings (temperature, humidity, battery) displayed on each card
- Activity log: sorted most-recent-first, timestamps formatted, color-coded by status
- Replaced browser alerts with inline card feedback
- Fixed critical bug: BLE scan was incorrectly marking all sensors Unavailable
- Fixed infinite loop when sensor sends no history notifications (90s timeout added)
- Fixed CSV timestamp format — now writes `YYYY-MM-DD HH:MM:SS` for correct Excel display
- Fixed battery percentage clamping (0–100%)
- Compiled EXE support via PyInstaller (frozen path resolution)
- Version number displayed in app header

### v2.0.0 — 2025-01-06
- Introduced GUI (Eel-based desktop interface)
- Scan, rename sensors, and fetch data via point-and-click

### v1.0.0
- Initial release — CLI-based BLE scanner and data fetcher

---

## Requirements

- Windows 10 / 11
- Python 3.10+ (if running from source)
- Bluetooth adapter with BLE support

---

<div align="center">

Made with ♥ by [Dr. Chun-I Chiu](https://github.com/TermCIC)

</div>
