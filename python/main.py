from irsdk import PitCommandMode, IRSDK
import sched
from utils import State, Car, MyQueue, time_it
import time
import numpy as np
from fastapi import FastAPI, WebSocket
import asyncio
import threading
import uvicorn
from datetime import datetime

app = FastAPI()

ir = IRSDK()
state = State()
FUEL_STRATEGY_LAPS = 5
fuel_consumption = MyQueue(FUEL_STRATEGY_LAPS)

# Shared car data
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
    "incidents": {
        "incidents": [],
        "total_incidents": 0,
    },
    "fast_repairs_used": 0,
}
data_lock = threading.Lock()

# @time_it
def split_time_info():
    with data_lock:
        shared_data_json["sectors"] = {(sector['SectorNum'] + 1): sector["SectorStartPct"] * 100 for sector in ir['SplitTimeInfo']['Sectors']}

# @time_it
def used_fast_repair():
    if state.fast_repairs_used != ir["PlayerFastRepairsUsed"]:
        state.fast_repairs_used = ir["PlayerFastRepairsUsed"]
        with data_lock:
            shared_data_json["fast_repairs_used"] = state.fast_repairs_used

# @time_it
def new_incidents():
    inc_diff = ir["PlayerCarMyIncidentCount"] - state.incidents
    if inc_diff > 0:
        state.incidents = ir["PlayerCarMyIncidentCount"]
        with data_lock:
            shared_data_json["incidents"]["total_incidents"] = state.incidents
            shared_data_json["incidents"]["incidents"].append((datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), inc_diff))

# @time_it
def weather_info():
    rad_to_deg = 57.296
    a = ir["WindDir"] * rad_to_deg
    angle = a + 22.5

    if angle > 0 and angle < 45:
        wind_direction = "North"
    elif angle >= 45 and angle < 90:
        wind_direction = "North-East"
    elif angle >= 90 and angle < 135:
        wind_direction = "East"
    elif angle >= 135 and angle < 180:
        wind_direction = "South-East"
    elif angle >= 180 and angle < 225:
        wind_direction = "South"
    elif angle >= 225 and angle < 270:
        wind_direction = "South-West"
    elif angle >= 270 and angle < 315:
        wind_direction = "West"
    elif angle >= 315 and angle < 360:
        wind_direction = "North-West"
    else:
        wind_direction = "Unknown direction"

    with data_lock:
        match ir['TrackWetness']:
            case 1:
                track_wetness = "Dry"
            case 2:
                track_wetness = "Mostly dry"
            case 3:
                track_wetness = "Very lightly wet"
            case 4:
                track_wetness = "Lightly wet"
            case 5:
                track_wetness = "Moderately wet"
            case 6:
                track_wetness = "Very wet"
            case 7:
                track_wetness = "Extremely wet"
            case _:
                track_wetness = "Unknown wetness"

        shared_data_json["weather"] = {
            "air_temp": ir['AirTemp'],
            "track_temp": ir['TrackTempCrew'],
            "wind_speed": ir['WindVel'] * 3.6,
            "wind_direction": f"{wind_direction} ({a:.2f}°)",
            "track_wetness": track_wetness,
            "precipitation": round(float(ir['Precipitation']), 2), 
            "declared_wet": ir['WeatherDeclaredWet'],
        }

# @time_it
def tyre_data():
    LF = {
        "left_carcass_temp": ir["LFtempCL"],
        "middle_carcass_temp": ir["LFtempCM"],
        "right_carcass_temp": ir["LFtempCR"],
        "left_tread_remaning": ir["LFwearL"] * 100,
        "middle_tread_remaning": ir["LFwearM"] * 100,
        "right_tread_remaning": ir["LFwearR"] * 100
    }

    
    RF = {
        "left_carcass_temp": ir["RFtempCL"],
        "middle_carcass_temp": ir["RFtempCM"],
        "right_carcass_temp": ir["RFtempCR"],
        "left_tread_remaning": ir["RFwearL"] * 100,
        "middle_tread_remaning": ir["RFwearM"] * 100,
        "right_tread_remaning": ir["RFwearR"] * 100
    }

    
    LR = {
        "left_carcass_temp": ir["LRtempCL"],
        "middle_carcass_temp": ir["LRtempCM"],
        "right_carcass_temp": ir["LRtempCR"],
        "left_tread_remaning": ir["LRwearL"] * 100,
        "middle_tread_remaning": ir["LRwearM"] * 100,
        "right_tread_remaning": ir["LRwearR"] * 100
    }

    
    RR = {
        "left_carcass_temp": ir["RRtempCL"],
        "middle_carcass_temp": ir["RRtempCM"],
        "right_carcass_temp": ir["RRtempCR"],
        "left_tread_remaning": ir["RRwearL"] * 100,
        "middle_tread_remaning": ir["RRwearM"] * 100,
        "right_tread_remaning": ir["RRwearR"] * 100
    }

    with data_lock:
        shared_data_json["tyres"]["front_left"] = LF
        shared_data_json["tyres"]["front_right"] = RF
        shared_data_json["tyres"]["rear_left"] = LR
        shared_data_json["tyres"]["rear_right"] = RR

# @time_it
def relative():
    ir.freeze_var_buffer_latest()
    all_cars = []
    for car in ir['DriverInfo']['Drivers']:
        all_cars.append(Car(car['CarIdx'], car['CarNumber'], car['UserName'], car['CarID'],
                             car['CarClassID'], car['CarScreenNameShort'], car['TeamName'],
                               car['IRating'], car['LicString']))
    all_cars.sort(key=lambda x: x.car_id)

    my_car_idx = ir['PlayerCarIdx']

    their_class = ir['CarIdxClass']
    their_position = ir['CarIdxPosition']
    their_lap = ir['CarIdxLap']
    their_distance_pct = ir['CarIdxLapDistPct']
    their_est_time = ir["CarIdxEstTime"]
    their_class_position = ir["CarIdxClassPosition"]
    them_pit_road = ir['CarIdxOnPitRoad']
    their_gap_leader = ir['CarIdxF2Time']
    their_last_lap = ir['CarIdxLastLapTime']

    them = list(zip(their_class, their_position, their_distance_pct, them_pit_road, their_lap, their_est_time, their_class_position, their_gap_leader, their_last_lap))

    car_data = []
    for car, elem in zip(all_cars, them):
        # Format last lap time to min:sec.ms format
        last_lap_time = elem[8]
        if last_lap_time > 0:
            minutes = int(last_lap_time / 60)
            seconds = int(last_lap_time % 60)
            milliseconds = int((last_lap_time % 1) * 1000)
            formatted_last_lap = f"{minutes}:{seconds:02d}.{milliseconds:03d}"
        else:
            formatted_last_lap = "--:--:---"
            
        car_data.append({
            "user_name": car.user_name,
            "team_name": car.team_name,
            "class_id": car.class_id,
            "car_model_id": car.car_model_id,
            "car_number": car.car_number,
            "car_class_position": elem[6],
            "gap_leader": elem[7],
            "car_position": elem[1],
            "car_est_time": elem[5],
            "distance_pct": elem[2],
            "in_pit": elem[3],
            "lap": elem[4],
            "last_lap": formatted_last_lap,
        })

    with data_lock:
        shared_data_json["player_car_number"] = all_cars[my_car_idx].car_number
        shared_data_json["cars"] = car_data

    ir.unfreeze_var_buffer_latest()

# @time_it
def check_if_in_pit():
    in_pit = ir['OnPitRoad']
    if in_pit:
        state.last_fuel_level = ir['FuelLevel']
        state.last_lap = ir['Lap']

# @time_it
def update_fuel_data():
    fuel_left = ir['FuelLevel']
    if state.last_fuel_level == -1.0:
        state.last_fuel_level = fuel_left
        return
    else:
        fuel_delta = state.last_fuel_level - fuel_left
        state.last_fuel_level = fuel_left
        fuel_consumption.put(fuel_delta)

    fuel_delta_avg = np.mean(fuel_consumption.queue)
    last_fuel_delta = fuel_consumption.last()

    full_laps_on_tank_from_avg = int(fuel_left / fuel_delta_avg)
    omlavg = full_laps_on_tank_from_avg + 1
    ollavg = full_laps_on_tank_from_avg - 1
    one_more_from_avg = fuel_left / omlavg
    one_less_from_avg = fuel_left / ollavg
    
    full_laps_on_tank_from_last = int(fuel_left / last_fuel_delta)

    fuel_analysis_dict = {
        "fuel_left": fuel_left,
        "average_consumption": fuel_delta_avg,
        "target_laps_avg": int(full_laps_on_tank_from_avg),
        "target_laps_avg_consumption": (fuel_left / full_laps_on_tank_from_avg),
        "ollavg": int(ollavg),
        "ollavg_consumption_target": one_less_from_avg,
        "omlavg": int(omlavg),
        "omlavg_consumption_target": one_more_from_avg,

        "last_lap_consumption": last_fuel_delta,
        "target_laps_last": int(full_laps_on_tank_from_last),
        "target_laps_last_consumption": (fuel_left / full_laps_on_tank_from_last),
    }

    with data_lock:
        shared_data_json["fuel_analysis"] = fuel_analysis_dict

def lap_finished():
    new_lap = ir['Lap']
    if new_lap is None or new_lap == 0:
        return False
    if new_lap == state.last_lap + 1:
        state.last_lap = new_lap
        print("Lap finished")
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
    # elif not state.ir_connected and ir.startup() and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
    return True

# @time_it
def execute_commands(text):
    commands = text.split(" ")
    ir.pit_command(PitCommandMode.clear)
    for command in commands:
        match command:
            case "lf":
                ir.pit_command(PitCommandMode.lf)
            case "rf":
                ir.pit_command(PitCommandMode.rf)
            case "lr":
                ir.pit_command(PitCommandMode.lr)
            case "rr":
                ir.pit_command(PitCommandMode.rr)
            case "fr":
                ir.pit_command(PitCommandMode.fr)
            case "ws":
                ir.pit_command(PitCommandMode.ws)
            case "clear_ws":
                ir.pit_command(PitCommandMode.clear_ws)
            case "clear_fr":
                ir.pit_command(PitCommandMode.clear_fr)
            case "clear_fuel":
                ir.pit_command(PitCommandMode.clear_fuel)
            case _:
                if "fuel" in command:
                    try:
                        fuel = int(command.split(".")[1])
                        ir.pit_command(PitCommandMode.fuel, fuel)
                    except ValueError:
                        print(f"Invalid fuel command: {command}")
                elif "tc" in command:
                    try:
                        tc = int(command.split(".")[1])
                        # ir.pit_command(PitCommandMode., tc) # cannot solve, need to use macros for tc
                    except ValueError:
                        print(f"Invalid tyre change command: {command}")

                else:
                    print(f"Unknown command: {command}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async def send_periodic_data():
        while True:
            await asyncio.sleep(1)
            with data_lock:
                try:
                    await websocket.send_json(shared_data_json)
                except Exception as e:
                    print(f"Send error: {e}")
                    break

    send_task = asyncio.create_task(send_periodic_data())
    try:
        while True:
            text = await websocket.receive_text()
            execute_commands(text)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        send_task.cancel()
        await websocket.close()


def new_session_setup():
    state.last_lap = ir['Lap']
    state.incidents = ir['PlayerCarMyIncidentCount']
    with data_lock:
        shared_data_json["incidents"]["total_incidents"] = state.incidents
    state.fast_repairs_used = ir["PlayerFastRepairsUsed"]
    split_time_info()

def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    threading.Thread(target=start_api, daemon=True).start()

    try:
        counter = 250 #remove counter
        while not check_iracing(f'./python/newdataset/data{counter}.bin'):
            pass
        print("iRacing connected")
        new_session_setup()
        while True:
            # to remove later #######
            if not check_iracing(f'./python/newdataset/data{counter}.bin') or not ir.is_initialized or not ir.is_connected:
                counter += 1
                if counter > 368:
                    counter = 1
                print("iRacing disconnected")
            # #########################
            # if not check_iracing() or not ir.is_initialized or not ir.is_connected:
            #     print("iRacing disconnected")
            if state.ir_connected:
                # check_if_in_pit()
                tyre_data()
                weather_info()
                # used_fast_repair()
                new_incidents()
                if lap_finished():
                    update_fuel_data()
                relative()
            ir.shutdown() # remove
            time.sleep(1)
    except KeyboardInterrupt:
        # press ctrl+c to exit
        pass