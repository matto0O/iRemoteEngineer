from irsdk import PitCommandMode, IRSDK
import time
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketState
import asyncio
import threading
import uvicorn
from datetime import datetime
from pyngrok import ngrok, conf
import tkinter as tk
import sys
import signal
import traceback

from iracing_gui import IracingDataGUI
from utils import MyQueue, State, Car, Config, TaskScheduler

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


exposed_port = 2137
ir = IRSDK()
state = State()
config = Config()
scheduler = TaskScheduler()

processing_thread = None
server_thread = None
ngrok_tunnel = None
gui = None
server = None
exit_event = threading.Event()

conf.set_default(conf.PyngrokConfig(ngrok_path="./_internal/ngrok.exe"))

FUEL_STRATEGY_LAPS = 5

fuel_consumption = MyQueue(FUEL_STRATEGY_LAPS)

shared_data_json = {
    "player_car_number": None,
    "cars": [],
    "fuel_analysis": {},
    "sectors": {},
    "weather": {},
    "tyres": {
        "front_left": {},
        "front_right": {},
        "rear_left": {},
        "rear_right": {}
    },
    "events": [],
    "total_incidents": 0,
    "fast_repairs_used": 0,
}
data_lock = threading.Lock()

def get_direction(angle=None):
    rad_to_deg = 57.296
    if angle is not None:
        angle_deg = angle
    else:
        angle_deg = ir["WindDir"] * rad_to_deg
    angle_middle = angle_deg + 22.5

    if 0 < angle_middle < 45:
        wind_direction = "North"
    elif 45 <= angle_middle < 90:
        wind_direction = "North-East"
    elif 90 <= angle_middle < 135:
        wind_direction = "East"
    elif 135 <= angle_middle < 180:
        wind_direction = "South-East"
    elif 180 <= angle_middle < 225:
        wind_direction = "South"
    elif 225 <= angle_middle < 270:
        wind_direction = "South-West"
    elif 270 <= angle_middle < 315:
        wind_direction = "West"
    elif 315 <= angle_middle < 360:
        wind_direction = "North-West"
    else:
        wind_direction = "Unknown direction"

    return wind_direction, angle_deg

def split_time_info():
    with data_lock:
        sectors = ir['SplitTimeInfo']['Sectors']
        shared_data_json["sectors"] = {(sector['SectorNum'] + 1): sector["SectorStartPct"] * 100 for sector in sectors}

def used_fast_repair():
    current_fast_repairs = ir["PlayerFastRepairsUsed"]
    if state.fast_repairs_used != current_fast_repairs:
        state.fast_repairs_used = current_fast_repairs
        current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        with data_lock:
            shared_data_json["fast_repairs_used"] = state.fast_repairs_used
            shared_data_json["events"].append({
                "type": "pit_stop",
                "description": "Used fast repair",
                "time": current_time,
            })

def new_incidents():
    current_incidents = ir["PlayerCarMyIncidentCount"]
    inc_diff = current_incidents - state.incidents
    if inc_diff > 0:
        state.incidents = current_incidents
        current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        with data_lock:
            shared_data_json["total_incidents"] = state.incidents
            shared_data_json["events"].append({
                "type": "incident",
                "description": f"Incurred {inc_diff}x incident",
                "time": current_time,
            })

def get_speed():
    return ir['WindVel'] * 3.6

def weather_info():
    wind_direction, angle = get_direction(ir['WindDir'] * 57.296)
    
    wetness_map = {
        1: "Dry",
        2: "Mostly dry",
        3: "Very lightly wet",
        4: "Lightly wet",
        5: "Moderately wet",
        6: "Very wet",
        7: "Extremely wet"
    }
    track_wetness = wetness_map.get(ir['TrackWetness'], "Unknown wetness")
    
    declared_wet = ir['WeatherDeclaredWet']
    speed = get_speed()
    current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    with data_lock:
        # Update weather data
        shared_data_json["weather"] = {
            "air_temp": ir['AirTemp'],
            "track_temp": ir['TrackTempCrew'],
            "wind_speed": speed,
            "wind_direction": f"{wind_direction} ({angle:.2f}°)",
            "track_wetness": track_wetness,
            "precipitation": round(float(ir['Precipitation']), 2), 
            "declared_wet": declared_wet,
        }

        # Check for track state change
        if declared_wet != state.track_state:
            event_description = f"Track state changed - {"Wet" if declared_wet else "Dry"}"
            shared_data_json["events"].append({
                "type": "weather",
                "time": current_time,
                "description": event_description,
            })
            state.track_state = declared_wet

        # Check for wind direction change
        if wind_direction != state.wind_direction:
            event_description = f"Wind direction changed from {state.wind_direction} to {wind_direction}"
            state.wind_direction = wind_direction
            shared_data_json["events"].append({
                "type": "weather",
                "time": current_time,
                "description": event_description,
            })

        # Check for wind speed change
        if state.wind_speed is None or abs(speed - state.wind_speed) > 5:
            event_description = f"Wind speed changed significantly to {speed:.2f}"
            state.wind_speed = speed
            shared_data_json["events"].append({
                "type": "weather",
                "time": current_time,
                "description": event_description,
            })

def tyre_data():
    def get_tyre_data(prefix):
        return {
            "left_carcass_temp": ir[f"{prefix}tempCL"],
            "middle_carcass_temp": ir[f"{prefix}tempCM"],
            "right_carcass_temp": ir[f"{prefix}tempCR"],
            "left_tread_remaning": ir[f"{prefix}wearL"] * 100,
            "middle_tread_remaning": ir[f"{prefix}wearM"] * 100,
            "right_tread_remaning": ir[f"{prefix}wearR"] * 100
        }

    with data_lock:
        shared_data_json["tyres"]["front_left"] = get_tyre_data("LF")
        shared_data_json["tyres"]["front_right"] = get_tyre_data("RF")
        shared_data_json["tyres"]["rear_left"] = get_tyre_data("LR")
        shared_data_json["tyres"]["rear_right"] = get_tyre_data("RR")

def relative():
    ir.freeze_var_buffer_latest()
    
    # Get all driver data once
    drivers = ir['DriverInfo']['Drivers']
    my_car_idx = ir['PlayerCarIdx']
    
    # Use list comprehension for better performance
    all_cars = [
        Car(car['CarIdx'], car['CarNumber'], car['UserName'], car['CarID'],
            car['CarClassID'], car['CarScreenNameShort'], car['TeamName'],
            car['IRating'], car['LicString']) for car in drivers
    ]
    all_cars.sort(key=lambda x: x.idx)

    # Get all arrays at once to minimize data access overhead
    their_position = ir['CarIdxPosition']
    their_lap = ir['CarIdxLap']
    their_distance_pct = ir['CarIdxLapDistPct']
    their_est_time = ir["CarIdxEstTime"]
    their_class_position = ir["CarIdxClassPosition"]
    them_pit_road = ir['CarIdxOnPitRoad']
    their_gap_leader = ir['CarIdxF2Time']
    their_last_lap = ir['CarIdxLastLapTime']

    ir.unfreeze_var_buffer_latest()
    # Format last lap time once for each car
    car_data = []
    for car, position, dist_pct, in_pit, lap, est_time, class_pos, gap_leader, last_lap in zip(
            all_cars, their_position, their_distance_pct, them_pit_road,
            their_lap, their_est_time, their_class_position, their_gap_leader, their_last_lap):

        # Format last lap time efficiently
        if last_lap > 0:
            minutes = int(last_lap / 60)
            seconds = int(last_lap % 60)
            milliseconds = int((last_lap % 1) * 1000)
            formatted_last_lap = f"{minutes}:{seconds:02d}.{milliseconds:03d}"
        else:
            formatted_last_lap = "--:--:---"
            
        car_data.append({
            "user_name": car.user_name,
            "team_name": car.team_name,
            "class_id": car.class_id,
            "car_model_id": car.car_model_id,
            "car_number": car.car_number,
            "car_class_position": class_pos,
            "gap_leader": gap_leader,
            "car_position": position,
            "car_est_time": est_time,
            "distance_pct": dist_pct,
            "in_pit": in_pit,
            "lap": lap,
            "last_lap": formatted_last_lap,
        })

    with data_lock:
        shared_data_json["player_car_number"] = all_cars[my_car_idx].car_number
        shared_data_json["cars"] = car_data

def check_if_in_pit():
    in_pit = ir['OnPitRoad']
    if state.in_pit != in_pit:
        state.in_pit = in_pit
        current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

        if in_pit:
            with data_lock:
                shared_data_json["events"].append({
                    "type": "pit_stop",
                    "description": "Entered the pit lane",
                    "time": current_time,
                })
        else:
            state.last_fuel_level = ir['FuelLevel']
            state.last_lap = ir['Lap']
            used_fast_repair()

            with data_lock:
                shared_data_json["events"].append({
                    "type": "pit_stop",
                    "description": "Left the pit lane",
                    "time": current_time,
                })

def update_fuel_data():
    fuel_left = ir['FuelLevel']
    if state.last_fuel_level == -1.0:
        state.last_fuel_level = fuel_left
        return
    
    fuel_delta = state.last_fuel_level - fuel_left
    state.last_fuel_level = fuel_left
    fuel_consumption.put(fuel_delta)

    # Use np.mean only on the actual data to avoid zeros
    if fuel_consumption.size > 0:
        fuel_delta_avg = np.mean(fuel_consumption.queue[:fuel_consumption.size])
    else:
        fuel_delta_avg = 0
        
    last_fuel_delta = fuel_consumption.last()

    # Avoid unnecessary calculations if fuel delta is zero
    if fuel_delta_avg > 0:
        full_laps_on_tank_from_avg = int(fuel_left / fuel_delta_avg)
        omlavg = full_laps_on_tank_from_avg + 1
        ollavg = max(1, full_laps_on_tank_from_avg - 1)  # Avoid division by zero
        one_more_from_avg = fuel_left / omlavg
        one_less_from_avg = fuel_left / ollavg
    else:
        full_laps_on_tank_from_avg = 0
        omlavg = 0
        ollavg = 0
        one_more_from_avg = 0
        one_less_from_avg = 0
    
    # Avoid division by zero
    if last_fuel_delta > 0:
        full_laps_on_tank_from_last = int(fuel_left / last_fuel_delta)
        target_laps_last_consumption = fuel_left / full_laps_on_tank_from_last
    else:
        full_laps_on_tank_from_last = 0
        target_laps_last_consumption = 0

    fuel_analysis_dict = {
        "fuel_left": fuel_left,
        "average_consumption": fuel_delta_avg,
        "target_laps_avg": int(full_laps_on_tank_from_avg),
        "target_laps_avg_consumption": (fuel_left / full_laps_on_tank_from_avg) if full_laps_on_tank_from_avg > 0 else 0,
        "ollavg": int(ollavg),
        "ollavg_consumption_target": one_less_from_avg,
        "omlavg": int(omlavg),
        "omlavg_consumption_target": one_more_from_avg,
        "last_lap_consumption": last_fuel_delta,
        "target_laps_last": int(full_laps_on_tank_from_last),
        "target_laps_last_consumption": target_laps_last_consumption,
    }

    with data_lock:
        shared_data_json["fuel_analysis"] = fuel_analysis_dict

def lap_finished():
    new_lap = ir['Lap']
    if new_lap is None or new_lap == 0:
        return False
    if new_lap == state.last_lap + 1:
        state.last_lap = new_lap
        return True
    state.last_lap = new_lap
    return False

def check_iracing(test_file=None):
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        state.last_car_setup_tick = -1
        ir.shutdown()
        return False
    elif not state.ir_connected and ir.startup(test_file=test_file) and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
    return True

def execute_commands(text):
    commands = text.split(" ")
    executed = ["clear"]
    ir.pit_command(PitCommandMode.clear)
    
    # Command mapping for better performance
    command_map = {
        "lf": PitCommandMode.lf,
        "rf": PitCommandMode.rf,
        "lr": PitCommandMode.lr,
        "rr": PitCommandMode.rr,
        "fr": PitCommandMode.fr,
        "ws": PitCommandMode.ws,
        "clear_ws": PitCommandMode.clear_ws,
        "clear_fr": PitCommandMode.clear_fr,
        "clear_fuel": PitCommandMode.clear_fuel,
    }
    
    for command in commands:
        if command in command_map:
            ir.pit_command(command_map[command])
            executed.append(command)
        elif "fuel" in command:
            try:
                fuel = int(command.split(".")[1])
                ir.pit_command(PitCommandMode.fuel, fuel)
                executed.append(f"fuel.{fuel}")
            except (ValueError, IndexError):
                print(f"Invalid fuel command: {command}")
        elif "tc" in command:
            try:
                tc = int(command.split(".")[1])
                # ir.pit_command(PitCommandMode., tc) # TODO cannot solve, need to use macros for tc
            except (ValueError, IndexError):
                print(f"Invalid tyre change command: {command}")
        else:
            print(f"Unknown command: {command}")

    current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    with data_lock:
        shared_data_json["events"].append({
            "type": "command",
            "description": f"Executed commands: {', '.join(executed)}",
            "time": current_time,
        })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection accepted")

    async def send_periodic_data():
        try:
            while True:
                await asyncio.sleep(1)
                with data_lock:
                    await websocket.send_json(shared_data_json)
        except Exception as e:
            print(f"Send error: {e}")
            return

    # Add endpoint for configuration updates
    async def handle_commands():
        return
    
    # Uncomment this block to enable command handling via WebSocket (May invite malicious commands)

        # while True:
        #     try:
        #         text = await websocket.receive_text()
        #         # Check if it's a configuration command
        #         if text.startswith("config:"):
        #             parts = text[7:].strip().split("=")
        #             if len(parts) == 2:
        #                 task_name, interval = parts
        #                 if config.update_interval(task_name, float(interval)):
        #                     # Re-register the task with the new interval
        #                     if task_name in scheduler.tasks and hasattr(globals(), task_name):
        #                         scheduler.register(task_name, globals()[task_name], config.get_interval(task_name))
        #                     await websocket.send_text(f"Updated {task_name} interval to {interval} seconds")
        #                 else:
        #                     await websocket.send_text(f"Unknown task: {task_name}")
        #             elif parts[0] == "loop" and len(parts) == 2:
        #                 config.set_loop_interval(float(parts[1]))
        #                 await websocket.send_text(f"Updated main loop interval to {parts[1]} seconds")
        #             else:
        #                 await websocket.send_text("Invalid config format. Use 'config:task_name=interval'")
        #         else:
        #             # Regular pit command
        #             execute_commands(text)
        #     except Exception as e:
        #         print(f"Command error: {e}")
        #         break

    send_task = asyncio.create_task(send_periodic_data())
    command_task = asyncio.create_task(handle_commands())
    
    try:
        await asyncio.gather(send_task, command_task)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        send_task.cancel()
        command_task.cancel()
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()

def new_session_setup():
    state.last_lap = ir['Lap']
    state.incidents = ir['PlayerCarMyIncidentCount']
    state.track_state = ir['WeatherDeclaredWet']
    state.wind_direction, _ = get_direction(ir['WindDir'] * 57.296)
    with data_lock:
        shared_data_json["total_incidents"] = state.incidents
    state.fast_repairs_used = ir["PlayerFastRepairsUsed"]
    split_time_info()

def start_api():
    global ngrok_tunnel
    try:
        ngrok_config = {
            "addr": f"localhost:{exposed_port}",
            "proto": "http",
            "bind_tls": True
        }
        ngrok_tunnel = ngrok.connect(**ngrok_config)
        print("Public URL:", ngrok_tunnel.public_url)
        if gui:
            gui.message_queue.put(("info", f"Server started at {ngrok_tunnel.public_url}"))
        return ngrok_tunnel.public_url
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        if gui:
            gui.message_queue.put(("error", f"Failed to start ngrok: {e}"))
        return None
    
def start_server(test_mode=False):
    global server_thread, server, processing_thread
    try:
        processing_thread = threading.Thread(
            target=data_processing_loop, 
            args=(test_mode,),
            daemon=True
        )
        processing_thread.start()
        time.sleep(1)

        config = uvicorn.Config(
            app, 
            host="0.0.0.0", 
            port=exposed_port, 
            access_log=False,
            reload=False,
            log_config=None,
        )
        
        # Start the server in a new thread
        server = uvicorn.Server(config)
        server_thread = threading.Thread(target=server.run, daemon=True)
        server_thread.start()
        
        # Wait a moment for the server to start
        time.sleep(1)
        
        # Now start the ngrok tunnel
        return start_api()
    except Exception as e:
        print(f"Error starting server: {e}")
        if gui:
            gui.message_queue.put(("error", f"Failed to start server: {traceback.format_exc()}"))
        if server_thread:
            server_thread.join(timeout=1)
            server_thread = None
        if server:
            server.should_exit = True
            server = None
        return None

def stop_server():
    global server_thread, ngrok_tunnel, server, processing_thread
    try:
        if processing_thread:
            processing_thread.join(timeout=1)
            processing_thread = None
            print("Processing thread stopped")

        if ngrok_tunnel:
            ngrok.disconnect(ngrok_tunnel.public_url)
            ngrok_tunnel = None
            print("Ngrok tunnel closed")
        
        if server:
            server.should_exit = True
            server = None
            print("Server stopped")

        if server_thread:
            server_thread.join(timeout=1)
            server_thread = None
            print("Server thread stopped")
    except Exception as e:
        print(f"Error stopping server: {e}")
        if gui:
            gui.message_queue.put(("error", f"Error stopping server: {e}"))

def register_scheduled_tasks():
    """Register all tasks with their configured intervals"""
    scheduler.register('relative', relative, config.get_interval('relative'))
    scheduler.register('check_if_in_pit', check_if_in_pit, config.get_interval('check_if_in_pit'))
    scheduler.register('weather_info', weather_info, config.get_interval('weather_info'))
    scheduler.register('new_incidents', new_incidents, config.get_interval('new_incidents'))
    scheduler.register('tyre_data', tyre_data, config.get_interval('tyre_data'))

def data_processing_loop(test_mode=True):
    try:
        # Initialize iRacing connection based on mode
        if test_mode:
            counter = 220  # for test mode
            while not check_iracing(f'./_internal/newdataset/data{counter}.bin'):
                if exit_event.is_set():
                    return
                time.sleep(0.5)
        else:
            while not check_iracing():
                if exit_event.is_set():
                    return
                time.sleep(0.5)
        
        new_session_setup()
        
        # Register all scheduled tasks
        register_scheduled_tasks()
        
        while not exit_event.is_set():
            # Check connection based on mode
            if test_mode:
                if check_iracing(f'./_internal/newdataset/data{counter}.bin') and ir.is_initialized and ir.is_connected:
                    counter += 1
                    if counter > 368:
                        counter = 1
                    
                    # Run scheduled tasks
                    scheduler.run_due_tasks()
                    
                    # Check for completed laps - this is event-based, not time-based
                    if lap_finished():
                        update_fuel_data()
                        tyre_data()  # Force update tire data on lap completion regardless of schedule
                    
                    ir.shutdown()  # Only for test mode
            else:
                if check_iracing() and ir.is_initialized and ir.is_connected:
                    # Run scheduled tasks
                    scheduler.run_due_tasks()
                    
                    # Check for completed laps - this is event-based, not time-based
                    if lap_finished():
                        update_fuel_data()
                        tyre_data()
            
            time.sleep(config.loop_interval)
    except Exception as e:
        print(f"Error in data processing: {e}")
        if gui:
            gui.message_queue.put(("error", f"Data processing error: {traceback.format_exc()}"))

def init_gui():
    global gui
    
    root = tk.Tk()
    gui = IracingDataGUI(root)
    
    # Set callbacks
    gui.set_callbacks({
        "start_server": start_live_mode,
        "stop_server": stop_server,
        "start_test_mode": start_test_mode,
        "stop_test_mode": stop_server,
        "update_interval": update_interval,
        "get_config": lambda: config
    })
    
    # Populate intervals once config is loaded
    gui.populate_intervals_tab()
    
    # Setup signal handlers for graceful shutdown
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, signal_handler)
    
    # Run the GUI
    gui.run()

def update_interval(task_name, interval):
    if task_name == "loop":
        config.set_loop_interval(float(interval))
        return True
    else:
        success = config.update_interval(task_name, float(interval))
        if success and task_name in scheduler.tasks:
            # Re-register the task with the new interval
            func = scheduler.tasks[task_name]["function"]
            scheduler.register(task_name, func, interval)
        return success

# New function to handle shutdown signals
def signal_handler(sig, frame):
    print("Shutting down...")
    exit_event.set()
    stop_server()
    sys.exit(0)

def start_live_mode():
    return start_server(test_mode=False)

def start_test_mode():
    return start_server(test_mode=True)

if __name__ == '__main__':
    init_gui()