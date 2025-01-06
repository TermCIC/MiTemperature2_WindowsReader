import threading
from bottle import Bottle, _stderr
# Suppress bottle's built-in logging of HTTP requests
class SilentBottle(Bottle):
    def _handle(self, environ):
        """Override _handle to suppress logging."""
        result = super(SilentBottle, self)._handle(environ)
        return result
import eel
eel.bottle = SilentBottle()
from backend import *
from random import randint

save_tasks_to_json({})

eel.init("web")

# Global variables
event_loop = None
background_task = None

# Start the event loop in a separate thread
def start_event_loop():
    global event_loop
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_forever()

# Run the event loop in a background thread
threading.Thread(target=start_event_loop, daemon=True).start()

@eel.expose
def scan():
    global background_task
    if background_task is None or background_task.done():
        background_task = asyncio.run_coroutine_threadsafe(run_in_background(), event_loop)

async def run_in_background():
    try:
        existing_devices = read_devices_from_json()
        await scan_ble_devices(existing_devices)  # Call your asynchronous run function
    except Exception as e:
        print(f"Error in background task: {e}")


@eel.expose
def update_status():
    ensure_file_exists()
    # Read sensors data
    sensors = read_devices_from_json()
    sensors_json = json.dumps(sensors)
    # Read tasks data
    tasks = read_tasks_from_json()
    tasks_json = json.dumps(tasks)
    # Combine sensors and logs into a single dictionary
    result = {
        "sensors": sensors_json,
        "tasks": tasks_json
    }
    # Return as JSON string
    return json.dumps(result)


@eel.expose
def change_name(address, newName):
    sensors = read_devices_from_json()
    sensors[address]["name"] = newName
    save_devices_to_json(sensors)
    tasks = read_tasks_from_json()
    timestamp = str(int(time()))  # Use time.time() and convert to a string
    tasks[timestamp] = {
        "task_type": "Change sensor name",
        "status": "finished"
    }
    save_tasks_to_json(tasks)


@eel.expose
def fetch_data(address, name):
    global event_loop  # Use the event loop created in the background thread
    if event_loop is None:
        raise RuntimeError("Event loop is not running. Ensure the event loop thread has started.")

    # Run the coroutine in the existing event loop
    asyncio.run_coroutine_threadsafe(fetch(address, name), event_loop)


# Start the index.html file
eel.start("ui.html")

