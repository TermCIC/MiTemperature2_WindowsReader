import asyncio
import csv
import json
import os
import struct
from datetime import datetime
from time import time

from bleak import BleakClient, BleakScanner, BleakError

history_data = {}

UUID_UNITS = 'EBE0CCBE-7A0A-4B0C-8A1A-6FF2997DA3A6'  # 0x00 - F, 0x01 - C    READ WRITE
UUID_HISTORY = 'ebe0ccbc-7a0a-4b0c-8a1a-6ff2997da3a6'  # Last idx 152          READ NOTIFY
UUID_TIME = 'EBE0CCB7-7A0A-4B0C-8A1A-6FF2997DA3A6'  # 5 or 4 bytes          READ WRITE
UUID_DATA = 'ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6'  # 3 bytes               READ NOTIFY
UUID_BATTERY = 'EBE0CCC4-7A0A-4B0C-8A1A-6FF2997DA3A6'  # 1 byte                READ
UUID_NUM_RECORDS = 'EBE0CCB9-7A0A-4B0C-8A1A-6FF2997DA3A6'  # 8 bytes               READ
UUID_RECORD_IDX = 'EBE0CCBA-7A0A-4B0C-8A1A-6FF2997DA3A6'  # 4 bytes               READ WRITE


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
        self.current_reads = None

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

    def process_current_reads(self, sensor_current_reads):
        if not self.current_reads:
            current_temperature = int.from_bytes(sensor_current_reads[0:2], byteorder="little", signed=True) / 100
            current_humidity = int.from_bytes(sensor_current_reads[2:3], byteorder="little", signed=True)
            current_voltage = int.from_bytes(sensor_current_reads[3:5], byteorder="little", signed=True) / 1000
            current_battery = round((current_voltage - 2) / (3.261 - 2) * 100, 2)
            self.current_reads = {
                "Temperature": current_temperature,
                "Humidity": current_humidity,
                "Voltage": current_voltage,
                "Battery": current_battery
            }
            print(
                f"Sensor status: Temperature: {current_temperature}, RH: {current_humidity}%, Battery: {current_battery}%")
        return self.current_reads

    def is_data_stale(self, stale_after_seconds=10):
        if self._last_notification_time is None:
            return False
        return (time() - self._last_notification_time) > stale_after_seconds


async def main(address, selected_device_name, max_retries=10):
    handler = BLEDeviceHandler()
    retries = 0
    while retries < max_retries:
        try:
            print(f"Trying to connect {address}")
            async with BleakClient(address) as client:
                print("Connected to:", address)

                # set time
                sensor_time_pass = await client.read_gatt_char(UUID_TIME)
                handler.start_time(sensor_time_pass)

                # current reads
                sensor_current_reads = await client.read_gatt_char(UUID_DATA)
                handler.process_current_reads(sensor_current_reads)

                # Set up the handler for history data
                await client.start_notify(UUID_HISTORY, handler.process_history_data)

                # Keep the program running to receive notifications
                while not handler.is_data_stale(stale_after_seconds=10):
                    await asyncio.sleep(1)

                # Stop notifications
                await client.stop_notify(UUID_HISTORY)
                HISTORICAL_DATA_CSV = f"DATA_name_{selected_device_name}_t_{int(time())}.csv"
                with open(HISTORICAL_DATA_CSV, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    # Write headers (optional)
                    writer.writerow(['Index', 'Timestamp', 'Min Temp', 'Max Temp', 'Min Humidity', 'Max Humidity'])
                    # Write data
                    writer.writerows(handler.historical_data)
                print(f"Saved historical data to {HISTORICAL_DATA_CSV}")
                return
        except (BleakError, asyncio.TimeoutError) as e:
            print(f"Connection failed: {e}. Retrying ({retries + 1}/{max_retries})...")
            retries += 1
            await asyncio.sleep(5)

    print("Failed to connect after several attempts.")


async def scan_ble_devices(existing_devices, scan_duration=30):
    print("Scanning sensors...(30 seconds)")
    devices = await BleakScanner.discover(timeout=scan_duration)
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
            print("\nAvailable Devices:")
            for idx, (address, name) in enumerate(devices):
                print(f"{idx}: {name or 'Unknown'} ({address})")
            print(f"{len(devices)}: Rescan devices")

            try:
                selected_index = int(input("Enter the number of the device to connect (or rescan): "))
                if 0 <= selected_index < len(devices):
                    selected_device_address, selected_device_name = devices[selected_index]
                    print(f"-> {selected_device_address} is selected")

                    if selected_device_name is None:
                        new_name = input("Enter a name for this device: ").strip()
                        existing_devices[selected_device_address]["name"] = new_name
                        save_devices_to_json(existing_devices)
                        selected_device_name = new_name

                    await main(selected_device_address, selected_device_name)
                    break  # success, break loop
                elif selected_index == len(devices):
                    print("Rescanning devices...")
                    continue
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")
        else:
            print("No Mi T/H Sensors found. Retrying in 1 second...")
            await asyncio.sleep(1)


asyncio.run(run())
