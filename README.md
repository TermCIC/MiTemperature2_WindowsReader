# ReadMi
## Windows-Compatible BLE Sensor Data Logger for Xiaomi LYWSD03MMC Sensors

ReadMi aims to allow Windows users to fetch environmental monitoring data from Xiaomi LYWSD03MMC sensors, which is a light weight and super cheap BLE Temperature/humidity sensor. This software allows you to turn your LYWSD03MMC sensors into dataloggers for your research.

<p align="center">
  <img src="https://github.com/TermCIC/MiTemperature2_WindowsReader/assets/32321661/008159ab-862c-459a-854d-f261d8ef7dd1" width="256" align="center">
  <img src="https://github.com/TermCIC/MiTemperature2_WindowsReader/assets/32321661/42409374-1218-45f3-8ff4-001a33c0e85d" width="256" align="center">
  <img src="https://github.com/TermCIC/MiTemperature2_WindowsReader/assets/32321661/76909a2c-c337-4bcd-9b52-010fbf21e7bf" width="256" align="center">
</p>

### Why choose Xiaomi LYWSD03MMC?
The cost of this sensor is ~5 USD dollars

### Sensor modification
You can connect the sensor to two AA batteries, ensuring that it operates for over a year, making it suitable for use with a datalogger.

### Program details
Language: 100% Python,
Library used: Bleak, asyncio

### How to use
That's all. Just ensure you have Python 3.7+ installed

```
pip install bleak
```

then run
```
ReadMiPlease.py
```

Or, you can just download the release binary "ReadMiPlease v1.0.0"

The program would scan sensors in your surrounding area, a json file is created to save names for sensors, then ask you to choose one of the sensor:
<br>
<img width="329" alt="image" src="https://github.com/TermCIC/MiTemperature2_WindowsReader/assets/32321661/f73aee2a-0e71-4ddf-a58b-dc6b6cb30512" align="center">

Request to record a name for selected sensor:
<br>
<img width="344" alt="image" src="https://github.com/TermCIC/MiTemperature2_WindowsReader/assets/32321661/0671312c-4e37-4817-8bd3-beed3d020aaf" align="center">

Then retreive the data...
<br>
<img width="462" alt="image" src="https://github.com/TermCIC/MiTemperature2_WindowsReader/assets/32321661/c179abff-0200-4dfd-963f-c889435914b5" align="center">

A csv file is created in the same folder of the program:
<br>
<img width="134" alt="image" src="https://github.com/TermCIC/MiTemperature2_WindowsReader/assets/32321661/bf904ad4-59e0-460f-a3c4-d13d62d4f137" align="center">

Done!
