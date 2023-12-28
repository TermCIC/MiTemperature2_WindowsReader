# Read data from Xiaomi Mijia LYWSD03MMC Bluetooth 4.2 Temperature Humidity sensor in Windows

import asyncio
import json
import os
import struct
from datetime import datetime
from time import time
import csv
from bleak import BleakClient, BleakScanner, BleakError

history_data = {}

UUID_UNITS = 'EBE0CCBE-7A0A-4B0C-8A1A-6FF2997DA3A6'  # 0x00 - F, 0x01 - C    READ WRITE
UUID_HISTORY = 'ebe0ccbc-7a0a-4b0c-8a1a-6ff2997da3a6'  # Last idx 152          READ NOTIFY
UUID_TIME = 'EBE0CCB7-7A0A-4B0C-8A1A-6FF2997DA3A6'  # 5 or 4 bytes          READ WRITE
UUID_DATA = 'ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6'  # 3 bytes               READ NOTIFY
UUID_BATTERY = 'EBE0CCC4-7A0A-4B0C-8A1A-6FF2997DA3A6'  # 1 byte                READ
UUID_NUM_RECORDS = 'EBE0CCB9-7A0A-4B0C-8A1A-6FF2997DA3A6'  # 8 bytes               READ
UUID_RECORD_IDX = 'EBE0CCBA-7A0A-4B0C-8A1A-6FF2997DA3A6'  # 4 bytes               READ WRITE

HISTORICAL_DATA_CSV = "historical_data.csv"


def ensure_file_exists():
    filename = "sensors.json"
    # Check if the file exists
    if not os.path.exists(filename):
        # If not, create it with an empty list as content
        with open(filename, "w") as file:
            json.dump({}, file)
        print(f"'{filename}' file created.")
    else:
        print(f"'{filename}' file already exists.")


# Read existing devices from the JSON file
def read_devices_from_json(filename="sensors.json"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    else:
        return {}


# Save the devices list to a JSON file
def save_devices_to_json(devices, filename="sensors.json"):
    with open(filename, "w") as file:
        json.dump(devices, file, indent=4)
    print(f"Saved {len(devices)} device(s) to {filename}")


# Assuming these methods are part of a class
class BLEDeviceHandler:
    def __init__(self):
        self._start_time = None
        self._last_notification_time = None
        self.tz_offset = 0  # Set your timezone offset here
        self.historical_data = []

    def process_history_data(self, sender, data):
        (idx, ts, max_temp, max_hum, min_temp, min_hum) = struct.unpack_from('<IIhBhB', data)
        ts = self._start_time + ts
        ts_date_time = datetime.fromtimestamp(ts)
        ts_date_time = str(ts_date_time)
        min_temp /= 10
        max_temp /= 10
        history_data[idx] = [ts_date_time, min_temp, min_hum, max_temp, max_hum]
        print(f"History Data at index {idx}: {history_data[idx]}")
        self._last_notification_time = time()
        self.historical_data.append([idx, ts_date_time, min_temp, max_temp, min_hum, max_hum])

    def start_time(self, sensor_time_pass):
        if not self._start_time:
            sensor_time_pass = int.from_bytes(sensor_time_pass, byteorder="little", signed=True)
            sensor_start_time = time() - sensor_time_pass
            self._start_time = sensor_start_time
        return self._start_time

    def is_data_stale(self, stale_after_seconds=10):
        if self._last_notification_time is None:
            return False
        return (time() - self._last_notification_time) > stale_after_seconds


async def main(address, max_retries=5):
    handler = BLEDeviceHandler()
    retries = 0
    while retries < max_retries:
        try:
            print(f"Trying to connect {address}")
            async with BleakClient(address) as client:
                print("Connected to:", address)
                sensor_time_pass = await client.read_gatt_char(UUID_TIME)
                handler.start_time(sensor_time_pass)
                # Set up the handler for history data
                await client.start_notify(UUID_HISTORY, handler.process_history_data)

                # Keep the program running to receive notifications
                while not handler.is_data_stale(stale_after_seconds=10):
                    await asyncio.sleep(1)

                # Stop notifications
                await client.stop_notify(UUID_HISTORY)
                with open(HISTORICAL_DATA_CSV, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    # Write headers (optional)
                    writer.writerow(['Index', 'Timestamp', 'Min Temp', 'Min Humidity', 'Max Temp', 'Max Humidity'])
                    # Write data
                    writer.writerows(handler.historical_data)
                print(f"Saved historical data to {HISTORICAL_DATA_CSV}")
                return
        except (BleakError, asyncio.TimeoutError) as e:
            print(f"Connection failed: {e}. Retrying ({retries + 1}/{max_retries})...")
            retries += 1
            await asyncio.sleep(5)

    print("Failed to connect after several attempts.")


async def scan_ble_devices(existing_devices):
    devices = await BleakScanner.discover()
    for device in devices:
        if device.name == "LYWSD03MMC":
            if device.address not in existing_devices:
                existing_devices[device.address] = {
                    "address": device.address,
                    "name": None
                }
                device.name = None
            else:
                for d in existing_devices:
                    if device.address == d:
                        device.name = existing_devices[d].get("name")

    save_devices_to_json(existing_devices)

    return [(device.address, device.name) for device in devices if device.address in existing_devices]


async def run():
    ensure_file_exists()
    while True:
        existing_devices = read_devices_from_json()
        devices = await scan_ble_devices(existing_devices)
        if devices:
            # Display the list of devices
            for idx, (address, name) in enumerate(devices):
                print(f"{idx}: {name or 'Unknown'} ({address})")

            # Ask the user to choose a device
            selected_index = int(input("Enter the number of the device to connect: "))
            if 0 <= selected_index < len(devices):
                selected_device_address, selected_device_name = devices[selected_index]

                print(f"-> {selected_device_address} is selected")

                # If the name is None, ask the user to input a name
                if selected_device_name is None:
                    new_name = input("Enter a name for this device: ").strip()
                    # Update the existing devices list with the new name
                    existing_devices[selected_device_address]["name"] = new_name
                    save_devices_to_json(existing_devices)

                await main(selected_device_address)
                break  # success, break loop
            else:
                print("Invalid selection.")
        else:
            print("No Mi T/H Sensors found. Retrying in 1 second...")
            await asyncio.sleep(1)


asyncio.run(run())
